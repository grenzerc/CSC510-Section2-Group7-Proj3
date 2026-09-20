package FoodSeer.controller;

import FoodSeer.config.SpringSecurityConfig;
import FoodSeer.dto.OrderDto;
import FoodSeer.entity.User;
import FoodSeer.repositories.UserRepository;
import FoodSeer.security.CustomUserDetailsService;
import FoodSeer.security.DriverStatsAccess;
import FoodSeer.security.JwtAuthenticationFilter;
import FoodSeer.security.JwtTokenProvider;
import FoodSeer.service.OrderService;
import FoodSeer.service.impl.JwtAccessDeniedHandler;
import FoodSeer.service.impl.JwtAuthenticationEntryPoint;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Real authentication, JWT filters and method security for
 * GET /api/orders/activeOrders/{username}; no database or server needed.
 *
 * The endpoint's @PreAuthorize previously had no enforcement at all (the
 * annotation was commented out), so any caller could read any driver's
 * active orders by guessing a username. This mirrors DriverStatsSecurityTest,
 * reusing the same DriverStatsAccess ownership resolver.
 */
@WebMvcTest(value = OrderController.class, properties = {
    "app.jwt-secret=Zm9vZHNlZXItdGVzdC1vbmx5LXNpZ25pbmcta2V5LTMyaXRlbXM=",
    "app.jwt-expiration-milliseconds=60000"
})
@Import({SpringSecurityConfig.class, JwtAuthenticationFilter.class, JwtTokenProvider.class,
    CustomUserDetailsService.class, DriverStatsAccess.class,
    JwtAuthenticationEntryPoint.class, JwtAccessDeniedHandler.class})
class OrderActiveOrdersSecurityTest {
    @Autowired private MockMvc mvc;
    @Autowired private AuthenticationManager authenticationManager;
    @Autowired private JwtTokenProvider tokenProvider;
    @Autowired private PasswordEncoder passwordEncoder;
    @MockBean private UserRepository users;
    @MockBean private OrderService orderService;

    @BeforeEach
    void setUp() {
        String password = passwordEncoder.encode("test-password");
        for (String username : new String[]{"driver1", "driver2", "customer", "staff", "admin"}) {
            String role = username.startsWith("driver") ? "DRIVER" : username.toUpperCase();
            User user = User.builder().username(username).email(username + "@example.test")
                    .password(password).role("ROLE_" + role).build();
            when(users.findByUsernameOrEmail(username, username)).thenReturn(Optional.of(user));
        }
        when(orderService.getActiveOrders("driver1")).thenReturn(
                List.of(new OrderDto(1L, "driver1-order")));
        when(orderService.getActiveOrders("driver2")).thenReturn(
                List.of(new OrderDto(2L, "driver2-order")));
    }

    @ParameterizedTest
    @ValueSource(strings = {"driver1", "missing"})
    void anonymousRequestsAreDenied(String username) throws Exception {
        // /api/orders/** stays permitAll at the URL level (unlike /api/driverStats,
        // which was tightened to authenticated()), so denial happens in method
        // security and anonymous callers see 403 here, not 401 - consistent with
        // this controller's other method-secured-only endpoints (e.g. /my-orders).
        mvc.perform(get("/api/orders/activeOrders/{username}", username))
                .andExpect(status().isForbidden());
        verifyNoInteractions(orderService);
    }

    @ParameterizedTest
    @ValueSource(strings = {"customer", "staff", "driver2"})
    void unauthorizedAccountsCannotReadAnotherDriversActiveOrders(String login) throws Exception {
        mvc.perform(get("/api/orders/activeOrders/{username}", "driver1")
                        .header("Authorization", bearer(login)))
                .andExpect(status().isForbidden());
        verifyNoInteractions(orderService);
    }

    @ParameterizedTest
    @ValueSource(strings = {"driver1", "admin"})
    void ownerAndAdministratorCanReadTheActiveOrders(String login) throws Exception {
        mvc.perform(get("/api/orders/activeOrders/{username}", "driver1")
                        .header("Authorization", bearer(login)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("driver1-order"));
        verify(orderService).getActiveOrders("driver1");
    }

    @Test
    void secondDriverReceivesTheirOwnDistinctActiveOrders() throws Exception {
        mvc.perform(get("/api/orders/activeOrders/{username}", "driver2")
                        .header("Authorization", bearer("driver2")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("driver2-order"));
    }

    private String bearer(String login) {
        // Use production password authentication and signed JWTs, not mocked principals.
        var authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(login, "test-password"));
        return "Bearer " + tokenProvider.generateToken(authentication);
    }
}
