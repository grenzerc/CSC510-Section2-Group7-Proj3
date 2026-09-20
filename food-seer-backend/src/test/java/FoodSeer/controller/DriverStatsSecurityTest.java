package FoodSeer.controller;

import FoodSeer.config.SpringSecurityConfig;
import FoodSeer.dto.DriverStatsDto;
import FoodSeer.entity.User;
import FoodSeer.repositories.UserRepository;
import FoodSeer.security.CustomUserDetailsService;
import FoodSeer.security.DriverStatsAccess;
import FoodSeer.security.JwtAuthenticationFilter;
import FoodSeer.security.JwtTokenProvider;
import FoodSeer.service.DriverStatsService;
import FoodSeer.service.impl.JwtAccessDeniedHandler;
import FoodSeer.service.impl.JwtAuthenticationEntryPoint;
import java.math.BigDecimal;
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

/** Real authentication, JWT filters and method security; no database or server needed. */
@WebMvcTest(value = DriverStatsController.class, properties = {
    "app.jwt-secret=Zm9vZHNlZXItdGVzdC1vbmx5LXNpZ25pbmcta2V5LTMyaXRlbXM=",
    "app.jwt-expiration-milliseconds=60000"
})
@Import({SpringSecurityConfig.class, JwtAuthenticationFilter.class, JwtTokenProvider.class,
    CustomUserDetailsService.class, DriverStatsAccess.class,
    JwtAuthenticationEntryPoint.class, JwtAccessDeniedHandler.class})
class DriverStatsSecurityTest {
    @Autowired private MockMvc mvc;
    @Autowired private AuthenticationManager authenticationManager;
    @Autowired private JwtTokenProvider tokenProvider;
    @Autowired private PasswordEncoder passwordEncoder;
    @MockBean private UserRepository users;
    @MockBean private DriverStatsService statistics;

    @BeforeEach
    void setUp() {
        String password = passwordEncoder.encode("test-password");
        for (String username : new String[]{"driver1", "driver2", "customer", "staff", "admin"}) {
            String role = username.startsWith("driver") ? "DRIVER" : username.toUpperCase();
            User user = User.builder().username(username).email(username + "@example.test")
                    .password(password).role("ROLE_" + role).build();
            when(users.findByUsernameOrEmail(username, username)).thenReturn(Optional.of(user));
            when(users.findByUsernameOrEmail(user.getEmail(), user.getEmail())).thenReturn(Optional.of(user));
        }
        when(statistics.getDriverStats("driver1")).thenReturn(
                new DriverStatsDto("driver1", 7, new BigDecimal("84.50"), new BigDecimal("4.5"), 2));
        when(statistics.getDriverStats("driver2")).thenReturn(
                new DriverStatsDto("driver2", 3, new BigDecimal("31.25"), new BigDecimal("4.0"), 1));
    }

    @ParameterizedTest
    @ValueSource(strings = {"driver1", "missing"})
    void anonymousRequestsRequireLogin(String username) throws Exception {
        mvc.perform(get("/api/driverStats").param("username", username))
                .andExpect(status().isUnauthorized());
        verifyNoInteractions(statistics);
    }

    @ParameterizedTest
    @ValueSource(strings = {"customer", "staff", "driver2", "driver2@example.test"})
    void unauthorizedAccountsCannotReadAnotherDriversStatistics(String login) throws Exception {
        mvc.perform(get("/api/driverStats").param("username", "driver1")
                        .header("Authorization", bearer(login)))
                .andExpect(status().isForbidden());
        verifyNoInteractions(statistics);
    }

    @ParameterizedTest
    @ValueSource(strings = {"driver1", "driver1@example.test", "admin"})
    void ownerAndAdministratorReceiveTheCorrectStatistics(String login) throws Exception {
        mvc.perform(get("/api/driverStats").param("username", "driver1")
                        .header("Authorization", bearer(login)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("driver1"))
                .andExpect(jsonPath("$.totalDeliveries").value(7))
                .andExpect(jsonPath("$.totalEarning").value(84.50))
                .andExpect(jsonPath("$.activeOrders").value(2));
        verify(statistics).getDriverStats("driver1");
        verifyNoMoreInteractions(statistics);
    }

    @ParameterizedTest
    @ValueSource(strings = {"customer", "staff"})
    void ownershipAloneDoesNotGrantAccess(String login) throws Exception {
        mvc.perform(get("/api/driverStats").param("username", login)
                        .header("Authorization", bearer(login)))
                .andExpect(status().isForbidden());
        verifyNoInteractions(statistics);
    }

    @Test
    void secondDriverReceivesTheirOwnDistinctStatistics() throws Exception {
        mvc.perform(get("/api/driverStats").param("username", "driver2")
                        .header("Authorization", bearer("driver2")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("driver2"))
                .andExpect(jsonPath("$.totalDeliveries").value(3))
                .andExpect(jsonPath("$.totalEarning").value(31.25));
    }

    @Test
    void administratorGetsNotFoundForMissingStatistics() throws Exception {
        mvc.perform(get("/api/driverStats").param("username", "missing")
                        .header("Authorization", bearer("admin")))
                .andExpect(status().isNotFound());
    }

    @Test
    void driverCannotProbeAnUnknownUsername() throws Exception {
        mvc.perform(get("/api/driverStats").param("username", "missing")
                        .header("Authorization", bearer("driver1")))
                .andExpect(status().isForbidden());
        verifyNoInteractions(statistics);
    }

    private String bearer(String login) {
        // Use production password authentication and signed JWTs, not mocked principals.
        var authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(login, "test-password"));
        return "Bearer " + tokenProvider.generateToken(authentication);
    }
}
