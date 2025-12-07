package FoodSeer.frontend;

import FoodSeer.entity.Food;
import FoodSeer.entity.Order;
import FoodSeer.entity.User;
import FoodSeer.dto.RegisterRequestDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DashboardTest {

    private User user1;
    private User user2;
    private Food food1;
    private Food food2;
    private Food food3;
    private Order order1;
    private Order order2;

    @BeforeEach
    void setUp() {
        // --- USERS ---
        RegisterRequestDto dto1 = new RegisterRequestDto("alice", "alice@example.com", "password", "CUSTOMER");
        RegisterRequestDto dto2 = new RegisterRequestDto("bob", "bob@example.com", "password", "CUSTOMER");

        // Using placeholders for extra strings required by User constructor
        user1 = new User(dto1, "NA", "NA");
        user2 = new User(dto2, "NA", "NA");

        // --- FOODS ---
        food1 = new Food("Pizza", 10, 12, Arrays.asList("GLUTEN", "DAIRY"));
        food2 = new Food("Burger", 15, 8, Arrays.asList("GLUTEN"));
        food3 = new Food("Salad", 20, 5, Arrays.asList("NUTS"));

        // Add ratings
        food1.setRating(4.5);
        food2.setRating(3.8);
        food3.setRating(4.9);

        // --- ORDERS ---
        order1 = new Order(1L, "Order1");
        order1.setUser(user1);
        order1.setFoods(Arrays.asList(food1, food3));
        order1.setIsFulfilled(false);

        order2 = new Order(2L, "Order2");
        order2.setUser(user2);
        order2.setFoods(Arrays.asList(food2, food1));
        order2.setIsFulfilled(true);
    }

    @Test
    void testInventoryFoodCount() {
        List<Food> inventory = Arrays.asList(food1, food2, food3);
        assertEquals(3, inventory.size(), "Inventory should contain 3 foods");
    }


    @Test
    void testOrderFoodCount() {
        assertEquals(2, order1.getFoods().size(), "Order1 should have 2 food items");
        assertEquals(2, order2.getFoods().size(), "Order2 should have 2 food items");
    }

    @Test
    void testPendingAndFulfilledOrders() {
        List<Order> orders = Arrays.asList(order1, order2);
        long pending = orders.stream().filter(o -> !o.getIsFulfilled()).count();
        long fulfilled = orders.stream().filter(Order::getIsFulfilled).count();

        assertEquals(1, pending, "There should be 1 pending order");
        assertEquals(1, fulfilled, "There should be 1 fulfilled order");
    }

    @Test
    void testTotalRevenuePerOrder() {
        double revenueOrder1 = order1.getFoods().stream().mapToDouble(Food::getPrice).sum();
        double revenueOrder2 = order2.getFoods().stream().mapToDouble(Food::getPrice).sum();

        assertEquals(17, revenueOrder1, "Order1 revenue should be 17");
        assertEquals(20, revenueOrder2, "Order2 revenue should be 20");
    }
}
