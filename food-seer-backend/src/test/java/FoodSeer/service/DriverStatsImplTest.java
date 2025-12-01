package FoodSeer.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

import java.math.BigDecimal;
import java.util.Optional;

import FoodSeer.service.impl.DriverStatsImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.junit.jupiter.MockitoExtension;

import FoodSeer.dto.DriverStatsDto;
import FoodSeer.entity.DriverStats;
import FoodSeer.mapper.DriverStatsMapper;
import FoodSeer.repositories.DriverStatsRepository;

@ExtendWith(MockitoExtension.class)
class DriverStatsImplTest {

    @Mock
    private DriverStatsRepository driverStatsRepository;

    @InjectMocks
    private DriverStatsImpl driverStatsService;

    @Test
    void getDriverStats_returnsDto_whenFound() {
        String username = "driver1";
        DriverStats entity = new DriverStats();
        entity.setUsername(username);

        when(driverStatsRepository.findByUsername(eq(username))).thenReturn(Optional.of(entity));

        DriverStatsDto mockedDto = mock(DriverStatsDto.class);

        try (MockedStatic<DriverStatsMapper> mocked = mockStatic(DriverStatsMapper.class)) {
            mocked.when(() -> DriverStatsMapper.mapToDriverStatsDto(entity)).thenReturn(mockedDto);

            DriverStatsDto result = driverStatsService.getDriverStats(username);

            assertSame(mockedDto, result);
            verify(driverStatsRepository, times(1)).findByUsername(eq(username));
            mocked.verify(() -> DriverStatsMapper.mapToDriverStatsDto(entity), times(1));
        }
    }

    @Test
    void getDriverStats_returnsNull_whenNotFound() {
        String username = "unknown";
        when(driverStatsRepository.findByUsername(eq(username))).thenReturn(Optional.empty());

        DriverStatsDto result = driverStatsService.getDriverStats(username);

        assertNull(result);
        verify(driverStatsRepository, times(1)).findByUsername(eq(username));
    }

    @Test
    void updateTotalEarnings_noop_whenDriverNotFound() {
        String username = "missing";
        BigDecimal earnings = BigDecimal.valueOf(10);
        when(driverStatsRepository.findByUsername(eq(username))).thenReturn(Optional.empty());

        driverStatsService.updateTotalEarnings(username, earnings);

        verify(driverStatsRepository, times(1)).findByUsername(eq(username));
        verify(driverStatsRepository, never()).save(any());
    }

    @Test
    void updateTotalEarnings_updatesFields_andSaves_whenDriverFound() {
        String username = "driver2";
        DriverStats entity = new DriverStats();
        entity.setUsername(username);
        entity.setTotalEarnings(BigDecimal.valueOf(100));
        entity.setTotalDeliveries(5);

        when(driverStatsRepository.findByUsername(eq(username))).thenReturn(Optional.of(entity));
        when(driverStatsRepository.save(any(DriverStats.class))).thenAnswer(inv -> inv.getArgument(0));

        BigDecimal add = BigDecimal.valueOf(25);
        driverStatsService.updateTotalEarnings(username, add);

        ArgumentCaptor<DriverStats> captor = ArgumentCaptor.forClass(DriverStats.class);
        verify(driverStatsRepository, times(1)).save(captor.capture());
        DriverStats saved = captor.getValue();

        assertEquals(BigDecimal.valueOf(125), saved.getTotalEarnings());
        assertEquals(6, saved.getTotalDeliveries());
        assertEquals(username, saved.getUsername());
    }
}