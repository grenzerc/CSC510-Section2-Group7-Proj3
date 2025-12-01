package FoodSeer.mapper;

import FoodSeer.dto.DriverStatsDto;
import FoodSeer.entity.DriverStats;

public class DriverStatsMapper {

    public static DriverStatsDto mapToDriverStatsDto(final DriverStats driverStats) {
        if (driverStats == null) {
            return null;
        }
        return new DriverStatsDto(driverStats.getUsername(), driverStats.getTotalDeliveries(),
                driverStats.getTotalEarnings(), driverStats.getAverageRating(), driverStats.getActiveOrders());

    }

    public static DriverStats mapToDriverStats(final DriverStatsDto driverStatsDto){
        final DriverStats driverStats = new DriverStats();
        driverStats.setUsername(driverStatsDto.username());
        driverStats.setTotalDeliveries(driverStatsDto.totalDeliveries());
        driverStats.setTotalEarnings(driverStatsDto.totalEarning());
        driverStats.setAverageRating(driverStatsDto.averageRating());
        driverStats.setActiveOrders(driverStatsDto.activeOrders());
        return driverStats;
    }

}
