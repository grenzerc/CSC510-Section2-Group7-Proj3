package FoodSeer.repositories;

import FoodSeer.entity.DriverStats;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
public class DriverStatsRepositoryTest {

    @Autowired
    private DriverStatsRepository driverStatsRepository;

    private String driverStats1Id;
    private String driverStats2Id;

    @BeforeEach
    public void setup() {
        driverStatsRepository.deleteAll();

        final DriverStats d1 = new DriverStats();
        d1.setUsername( "driver1" );
        d1.setTotalDeliveries( 25 );
        d1.setTotalEarnings(BigDecimal.valueOf(150.50));
        d1.setAverageRating(BigDecimal.valueOf(4.5));
        driverStatsRepository.save( d1 );
        driverStats1Id = d1.getUsername();

        final DriverStats d2 = new DriverStats();
        d2.setUsername( "driver2" );
        d2.setTotalDeliveries( 10 );
        d2.setTotalEarnings(BigDecimal.valueOf(75.00));
        d2.setAverageRating(BigDecimal.valueOf(4.8));
        driverStatsRepository.save( d2 );
        driverStats2Id = d2.getUsername();
    }

    @Test
    @Transactional
    public void testAddDriverStats() {
        final DriverStats d1 = driverStatsRepository.findById( driverStats1Id ).get();
        assertAll( "Driver Stats 1 contents",
                () -> assertEquals( driverStats1Id, d1.getUsername() ),
                () -> assertEquals( "driver1", d1.getUsername() ),
                () -> assertEquals( 25, d1.getTotalDeliveries() ),
                () -> assertEquals(0, d1.getTotalEarnings().compareTo(new BigDecimal("150.50"))),
                () -> assertEquals( 0, d1.getAverageRating().compareTo(new BigDecimal("4.5")) ) );

        final DriverStats d2 = driverStatsRepository.findById( driverStats2Id ).get();
        assertAll( "Driver Stats 2 contents",
                () -> assertEquals( driverStats2Id, d2.getUsername() ),
                () -> assertEquals( "driver2", d2.getUsername() ),
                () -> assertEquals( 10, d2.getTotalDeliveries() ),
                () -> assertEquals( 0, d2.getTotalEarnings().compareTo(new BigDecimal("75.00")) ),
                () -> assertEquals( 0, d2.getAverageRating().compareTo(new BigDecimal("4.8")) ) );
    }


    @Test
    @Transactional
    public void testUpdateDriverStats() {
        final DriverStats d1 = driverStatsRepository.findById( driverStats1Id ).get();
        d1.setTotalDeliveries( 30 );
        d1.setTotalEarnings(BigDecimal.valueOf(200.75));
        d1.setAverageRating(BigDecimal.valueOf(4.7));
        driverStatsRepository.save( d1 );

        final DriverStats updated = driverStatsRepository.findById( driverStats1Id ).get();
        assertAll( "Updated Driver Stats",
                () -> assertEquals( driverStats1Id, updated.getUsername() ),
                () -> assertEquals( "driver1", updated.getUsername() ),
                () -> assertEquals( 30, updated.getTotalDeliveries() ),
                () -> assertEquals(0, updated.getTotalEarnings().compareTo(new BigDecimal("200.75"))),
                () -> assertEquals(0, updated.getAverageRating().compareTo(new BigDecimal("4.7"))) );
    }

    @Test
    @Transactional
    public void testDeleteDriverStats() {
        assertTrue( driverStatsRepository.findById( driverStats1Id ).isPresent() );

        driverStatsRepository.deleteById( driverStats1Id );

        assertFalse( driverStatsRepository.findById( driverStats1Id ).isPresent() );
        assertTrue( driverStatsRepository.findById( driverStats2Id ).isPresent() );
    }

}
