package FoodSeer.service.impl;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import FoodSeer.constant.IncidentSource;
import FoodSeer.entity.Food;
import FoodSeer.entity.Incident;
import FoodSeer.entity.Notification;
import FoodSeer.entity.Order;
import FoodSeer.entity.User;
import FoodSeer.exception.ResourceNotFoundException;
import FoodSeer.repositories.FoodRepository;
import FoodSeer.repositories.IncidentRepository;
import FoodSeer.repositories.NotificationRepository;
import FoodSeer.repositories.OrderRepository;
import FoodSeer.service.AllergenMatcher;
import FoodSeer.service.TraceResult;
import FoodSeer.service.TraceService;

/**
 * Default {@link TraceService}.
 *
 * The trace is by dish and time: an order is exposed if it contains a suspect
 * food and was placed inside the incident window. A customer is warned if they
 * own an exposed order and their saved restrictions overlap the allergen.
 * Orders with no recorded time (saved before the time field existed) are
 * skipped, because there is no way to say whether they fall inside the window.
 */
@Service
public class TraceServiceImpl implements TraceService {

    private final OrderRepository orderRepository;
    private final FoodRepository foodRepository;
    private final IncidentRepository incidentRepository;
    private final NotificationRepository notificationRepository;
    private final long windowHours;

    /**
     * Creates the service.
     *
     * @param orderRepository
     *            orders
     * @param foodRepository
     *            foods
     * @param incidentRepository
     *            incidents
     * @param notificationRepository
     *            notifications
     * @param windowHours
     *            for customer reports, hours before and after the order to
     *            search; set with foodseer.trace.window-hours, default 2
     */
    public TraceServiceImpl(final OrderRepository orderRepository, final FoodRepository foodRepository,
            final IncidentRepository incidentRepository, final NotificationRepository notificationRepository,
            @Value("${foodseer.trace.window-hours:2}") final long windowHours) {
        if (windowHours < 0) {
            throw new IllegalArgumentException("The trace window cannot be negative.");
        }
        this.orderRepository = orderRepository;
        this.foodRepository = foodRepository;
        this.incidentRepository = incidentRepository;
        this.notificationRepository = notificationRepository;
        this.windowHours = windowHours;
    }

    @Override
    @Transactional
    public TraceResult reportRestaurantIncident(final String reporterUsername, final String allergen,
            final List<Long> suspectFoodIds, final LocalDateTime windowStart, final LocalDateTime windowEnd) {
        requireReporter(reporterUsername);
        final String normalizedAllergen = requireAllergen(allergen);
        if (suspectFoodIds == null || suspectFoodIds.isEmpty()) {
            throw new IllegalArgumentException("At least one suspect food is required.");
        }
        if (windowStart == null || windowEnd == null) {
            throw new IllegalArgumentException("Both a window start and a window end are required.");
        }
        if (windowStart.isAfter(windowEnd)) {
            throw new IllegalArgumentException("The window start must not be after the window end.");
        }

        final List<Food> suspectFoods = loadFoods(suspectFoodIds);

        final Incident incident = new Incident();
        incident.setSource(IncidentSource.RESTAURANT);
        incident.setAllergen(normalizedAllergen);
        incident.setReporterUsername(reporterUsername);
        incident.setSourceOrderId(null);
        incident.setWindowStart(windowStart);
        incident.setWindowEnd(windowEnd);

        return traceAndNotify(incident, suspectFoods);
    }

    @Override
    @Transactional
    public TraceResult reportCustomerReaction(final String reporterUsername, final Long orderId,
            final String allergen) {
        requireReporter(reporterUsername);
        final String normalizedAllergen = requireAllergen(allergen);
        if (orderId == null) {
            throw new IllegalArgumentException("An order id is required.");
        }

        final Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new ResourceNotFoundException("Order does not exist with id " + orderId));

        final User owner = order.getUser();
        if (owner == null || !reporterUsername.equals(owner.getUsername())) {
            throw new AccessDeniedException("You can only report a reaction on your own order.");
        }
        if (order.getCreatedAt() == null) {
            throw new IllegalArgumentException("This order has no recorded time, so it cannot be traced.");
        }
        final List<Food> orderFoods = order.getFoods();
        if (orderFoods == null || orderFoods.isEmpty()) {
            throw new IllegalArgumentException("This order has no foods, so it cannot be traced.");
        }

        // Foods that declare the allergen are the suspects. If none do, the
        // allergen was not on the menu, so every food in the order is suspect.
        final List<Food> declaring = new ArrayList<>();
        for (final Food food : orderFoods) {
            if (AllergenMatcher.foodDeclaresAllergen(food.getAllergies(), normalizedAllergen)) {
                declaring.add(food);
            }
        }
        final List<Food> suspectFoods;
        if (declaring.isEmpty()) {
            suspectFoods = new ArrayList<>(orderFoods);
        } else {
            suspectFoods = declaring;
        }

        final Incident incident = new Incident();
        incident.setSource(IncidentSource.CUSTOMER);
        incident.setAllergen(normalizedAllergen);
        incident.setReporterUsername(reporterUsername);
        incident.setSourceOrderId(order.getId());
        incident.setWindowStart(order.getCreatedAt().minusHours(windowHours));
        incident.setWindowEnd(order.getCreatedAt().plusHours(windowHours));

        return traceAndNotify(incident, suspectFoods);
    }

    /**
     * Saves the incident, finds the exposed orders, and creates one
     * notification for each affected customer.
     *
     * @param incident
     *            the incident, with source, allergen, reporter and window set
     * @param suspectFoods
     *            the foods to search orders for
     * @return the trace result
     */
    private TraceResult traceAndNotify(final Incident incident, final List<Food> suspectFoods) {
        final Set<Long> suspectIds = new LinkedHashSet<>();
        for (final Food food : suspectFoods) {
            suspectIds.add(food.getId());
        }
        incident.setSuspectFoodIds(suspectIds);
        incident.setReportedAt(LocalDateTime.now());
        final Incident savedIncident = incidentRepository.save(incident);

        final List<Order> exposedOrders = findExposedOrders(suspectFoods, incident.getWindowStart(),
                incident.getWindowEnd());

        final List<Long> exposedOrderIds = new ArrayList<>();
        final Map<String, Notification> notificationByUser = new LinkedHashMap<>();

        for (final Order order : exposedOrders) {
            exposedOrderIds.add(order.getId());

            final User customer = order.getUser();
            if (customer == null) {
                continue;
            }
            final String username = customer.getUsername();
            if (username == null || username.equals(incident.getReporterUsername())) {
                continue;
            }
            if (notificationByUser.containsKey(username)) {
                continue;
            }
            if (!AllergenMatcher.restrictionsAffectedBy(customer.getDietaryRestrictions(),
                    incident.getAllergen())) {
                continue;
            }

            final Notification notification = new Notification();
            notification.setIncidentId(savedIncident.getId());
            notification.setOrderId(order.getId());
            notification.setRecipientUsername(username);
            notification.setMessage(buildMessage(order, suspectIds, incident.getAllergen()));
            notification.setCreatedAt(LocalDateTime.now());
            notification.setAcknowledged(false);
            notificationByUser.put(username, notification);
        }

        final List<Notification> notifications = new ArrayList<>(notificationByUser.values());
        if (!notifications.isEmpty()) {
            notificationRepository.saveAll(notifications);
        }
        return new TraceResult(savedIncident, exposedOrderIds, notifications);
    }

    /**
     * Finds orders that contain any suspect food and were placed inside the
     * window, each order once, oldest first.
     *
     * @param suspectFoods
     *            the foods to search for
     * @param windowStart
     *            start of the window, inclusive
     * @param windowEnd
     *            end of the window, inclusive
     * @return the exposed orders
     */
    private List<Order> findExposedOrders(final List<Food> suspectFoods, final LocalDateTime windowStart,
            final LocalDateTime windowEnd) {
        final Map<Long, Order> byId = new LinkedHashMap<>();
        for (final Food food : suspectFoods) {
            final List<Order> ordersWithFood = orderRepository.findOrdersContainingFood(food);
            if (ordersWithFood == null) {
                continue;
            }
            for (final Order order : ordersWithFood) {
                final LocalDateTime placedAt = order.getCreatedAt();
                if (placedAt == null) {
                    continue;
                }
                if (placedAt.isBefore(windowStart) || placedAt.isAfter(windowEnd)) {
                    continue;
                }
                if (!byId.containsKey(order.getId())) {
                    byId.put(order.getId(), order);
                }
            }
        }
        final List<Order> exposed = new ArrayList<>(byId.values());
        Collections.sort(exposed, Comparator.comparing(Order::getCreatedAt).thenComparing(Order::getId));
        return exposed;
    }

    /**
     * Builds the private notice. It names the customer's own order and dishes
     * only, never other customers or who filed the report.
     */
    private String buildMessage(final Order order, final Set<Long> suspectIds, final String allergen) {
        final List<String> dishNames = new ArrayList<>();
        for (final Food food : order.getFoods()) {
            if (suspectIds.contains(food.getId())) {
                dishNames.add(food.getFoodName());
            }
        }
        final String dishes = String.join(", ", dishNames);
        return "Food safety notice: your order #" + order.getId() + " (" + dishes + ") may have been exposed to "
                + allergen + ", which matches your saved allergy list. Please check with the restaurant before you"
                + " eat it.";
    }

    /**
     * Loads each food once, in the order given.
     */
    private List<Food> loadFoods(final List<Long> foodIds) {
        final Map<Long, Food> byId = new LinkedHashMap<>();
        for (final Long foodId : foodIds) {
            if (foodId == null) {
                throw new IllegalArgumentException("A suspect food id cannot be null.");
            }
            if (byId.containsKey(foodId)) {
                continue;
            }
            final Food food = foodRepository.findById(foodId)
                    .orElseThrow(() -> new ResourceNotFoundException("Food does not exist with id " + foodId));
            byId.put(foodId, food);
        }
        return new ArrayList<>(byId.values());
    }

    private void requireReporter(final String reporterUsername) {
        if (reporterUsername == null || reporterUsername.trim().isEmpty()) {
            throw new IllegalArgumentException("A reporter is required.");
        }
    }

    private String requireAllergen(final String allergen) {
        final String normalized = AllergenMatcher.normalizeTerm(allergen);
        if (normalized.isEmpty()) {
            throw new IllegalArgumentException("An allergen is required.");
        }
        return normalized;
    }
}
