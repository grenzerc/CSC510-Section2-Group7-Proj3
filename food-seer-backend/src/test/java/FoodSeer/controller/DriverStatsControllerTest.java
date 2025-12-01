package FoodSeer.controller;

import FoodSeer.dto.DriverStatsDto;
import FoodSeer.security.JwtTokenProvider;
import FoodSeer.service.DriverStatsService;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.eq;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(DriverStatsController.class)
@AutoConfigureMockMvc(addFilters = false)
class DriverStatsControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private DriverStatsService driverStatsService;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    void shouldReturnDriverStatsWhenServiceReturnsDto() throws Exception {
        DriverStatsDto mockDto = Mockito.mock(DriverStatsDto.class);
        Mockito.when(driverStatsService.getDriverStats(eq("driver1"))).thenReturn(mockDto);

        mockMvc.perform(get("/api/driverStats")
                        .param("username", "driver1"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON));
    }

    @Test
    void shouldReturnInternalServerErrorWhenServiceThrows() throws Exception {
        Mockito.when(driverStatsService.getDriverStats(eq("driver-error")))
                .thenThrow(new RuntimeException("service failure"));

        mockMvc.perform(get("/api/driverStats")
                        .param("username", "driver-error"))
                .andExpect(status().isInternalServerError());
    }
}
