package FoodSeer.service;

import FoodSeer.dto.DriverStatsDto;

import java.math.BigDecimal;

public interface DriverStatsService {

    DriverStatsDto getDriverStats(String username);
    void updateTotalEarnings(String username, BigDecimal earnings);
}
