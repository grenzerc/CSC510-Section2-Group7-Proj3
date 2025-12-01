package FoodSeer.service.impl;

import FoodSeer.dto.DriverStatsDto;
import FoodSeer.entity.DriverStats;
import FoodSeer.mapper.DriverStatsMapper;
import FoodSeer.repositories.DriverStatsRepository;
import FoodSeer.service.DriverStatsService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.Optional;

@Service
public class DriverStatsImpl implements DriverStatsService {

    private static final Logger logger = LoggerFactory.getLogger(DriverStatsImpl.class);

    @Autowired
    private DriverStatsRepository driverStatsRepository;

    @Override
    public DriverStatsDto getDriverStats(String username){
        logger.info("Getting driver stats for username: {}", username);
        Optional<DriverStats> driverStats = driverStatsRepository.findByUsername(username);
        if (driverStats.isEmpty()) {
            logger.info("The user {} does not exist in the database.", username);
            return null;
        }
        return DriverStatsMapper.mapToDriverStatsDto(driverStats.get());
    }

    @Override
    public void updateTotalEarnings(String username, BigDecimal earnings){
        logger.info("Updating total earning by: {}", earnings);
        Optional<DriverStats> optionalDriverStats = driverStatsRepository.findByUsername(username);
        if(optionalDriverStats.isEmpty()){
            logger.info("The user {} does not exist in the database", username);
            return;
        }
        DriverStats driverStats = optionalDriverStats.get();
        driverStats.setTotalEarnings(driverStats.getTotalEarnings().add(earnings));
        driverStats.setTotalDeliveries(driverStats.getTotalDeliveries() + 1);
        driverStatsRepository.save(driverStats);
    }
}
