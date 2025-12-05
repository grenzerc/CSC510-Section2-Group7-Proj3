// java
package FoodSeer.mapper;

import static org.junit.jupiter.api.Assertions.*;

import FoodSeer.dto.DriverStatsDto;
import FoodSeer.entity.DriverStats;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.math.BigDecimal;

class DriverStatsMapperTest {

    @Test
    void mapToDriverStatsDto_nullReturnsNull() {
        assertNull(DriverStatsMapper.mapToDriverStatsDto(null));
    }

    @Test
    void mapToDriverStatsDto_mapsAllFields() throws Exception {
        DriverStats ds = new DriverStats();
        ds.setUsername("driver1");
        ds.setTotalDeliveries(42);
        ds.setTotalEarnings(BigDecimal.valueOf(1234.56));
        ds.setAverageRating(BigDecimal.valueOf(4.7));
        ds.setActiveOrders(3);

        Object dto = DriverStatsMapper.mapToDriverStatsDto(ds);
        assertNotNull(dto, "DTO should not be null");

        // Read common getter/field names robustly
        String username = extractString(dto, new String[]{"username", "getUsername"});
        Integer totalDeliveries = extractInteger(dto, new String[]{"totalDeliveries", "getTotalDeliveries"});
        Double totalEarnings = extractDouble(dto, new String[]{"totalEarnings", "totalEarning", "getTotalEarnings", "getTotalEarning"});
        Double averageRating = extractDouble(dto, new String[]{"averageRating", "getAverageRating"});
        Integer activeOrders = extractInteger(dto, new String[]{"activeOrders", "getActiveOrders"});

        assertEquals("driver1", username);
        assertEquals(42, totalDeliveries.intValue());
        assertEquals(1234.56, totalEarnings, 0.0001);
        assertEquals(4.7, averageRating, 0.0001);
        assertEquals(3, activeOrders.intValue());
    }

    @Test
    void mapToDriverStats_mapsAllFields() throws Exception {
        // Create a DriverStatsDto instance via reflection (try common constructor shape)
        Class<?> dtoClass = Class.forName("FoodSeer.dto.DriverStatsDto");
        DriverStatsDto dto = new DriverStatsDto("driverX", 7, BigDecimal.valueOf(99.5), BigDecimal.valueOf(4.2), 1);
        assertNotNull(dto);

        DriverStats entity = DriverStatsMapper.mapToDriverStats(dto);
        assertNotNull(entity);

        assertEquals("driverX", safeCallString(entity, "getUsername"));
        assertEquals(7, safeCallInt(entity, "getTotalDeliveries"));
        assertEquals(99.5, safeCallDouble(entity, "getTotalEarnings"), 0.0001);
        assertEquals(4.2, safeCallDouble(entity, "getAverageRating"), 0.0001);
        assertEquals(1, safeCallInt(entity, "getActiveOrders"));
    }

    // --- reflection helpers ---

    private static Object instantiateDriverStatsDto(Class<?> dtoClass, String username, int totalDeliveries,
                                                    double totalEarnings, double averageRating, int activeOrders) throws Exception {
        // Try canonical constructor (String,int,double,double,int)
        Constructor<?> ctor = null;
        for (Constructor<?> c : dtoClass.getConstructors()) {
            if (c.getParameterCount() == 5) {
                ctor = c;
                break;
            }
        }
        if (ctor == null) {
            throw new IllegalStateException("No 5-arg constructor found on DriverStatsDto");
        }
        return ctor.newInstance(username, totalDeliveries, totalEarnings, averageRating, activeOrders);
    }

    private static String extractString(Object obj, String[] names) {
        Object val = extractValue(obj, names);
        return val == null ? null : val.toString();
    }

    private static Integer extractInteger(Object obj, String[] names) {
        Object val = extractValue(obj, names);
        if (val == null) return null;
        if (val instanceof Number) return ((Number) val).intValue();
        try { return Integer.parseInt(val.toString()); } catch (Exception e) { return null; }
    }

    private static Double extractDouble(Object obj, String[] names) {
        Object val = extractValue(obj, names);
        if (val == null) return null;
        if (val instanceof Number) return ((Number) val).doubleValue();
        try { return Double.parseDouble(val.toString()); } catch (Exception e) { return null; }
    }

    private static Object extractValue(Object obj, String[] names) {
        if (obj == null) return null;
        Class<?> c = obj.getClass();
        for (String n : names) {
            // try method
            try {
                Method m = c.getMethod(n);
                return m.invoke(obj);
            } catch (NoSuchMethodException ignored) {
            } catch (Exception ignored) {
            }
            // try field
            try {
                Field f = c.getDeclaredField(n);
                f.setAccessible(true);
                return f.get(obj);
            } catch (NoSuchFieldException ignored) {
            } catch (Exception ignored) {
            }
        }
        // fallback: inspect declared fields for first String/Number
        for (Field f : c.getDeclaredFields()) {
            try {
                f.setAccessible(true);
                Object v = f.get(obj);
                if (v instanceof String || v instanceof Number) return v;
            } catch (Exception ignored) {
            }
        }
        return null;
    }

    private static String safeCallString(Object obj, String methodName) {
        try {
            Method m = obj.getClass().getMethod(methodName);
            Object r = m.invoke(obj);
            return r == null ? null : r.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static int safeCallInt(Object obj, String methodName) {
        try {
            Method m = obj.getClass().getMethod(methodName);
            Object r = m.invoke(obj);
            return r instanceof Number ? ((Number) r).intValue() : Integer.parseInt(r.toString());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static double safeCallDouble(Object obj, String methodName) {
        try {
            Method m = obj.getClass().getMethod(methodName);
            Object r = m.invoke(obj);
            return r instanceof Number ? ((Number) r).doubleValue() : Double.parseDouble(r.toString());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
