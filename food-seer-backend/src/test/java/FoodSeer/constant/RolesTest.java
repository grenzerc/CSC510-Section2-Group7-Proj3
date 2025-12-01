// java
package FoodSeer.constant;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Modifier;

import static org.junit.jupiter.api.Assertions.*;

class RolesTest {

    @Test
    void constantsHaveExpectedValues() {
        assertEquals("ROLE_CUSTOMER", Roles.ROLE_CUSTOMER);
        assertEquals("ROLE_STAFF", Roles.ROLE_STAFF);
        assertEquals("ROLE_DRIVER", Roles.ROLE_DRIVER);
    }

    @Test
    void classIsFinalAndHasPrivateConstructor() throws Exception {
        // Class should be final
        assertTrue(Modifier.isFinal(Roles.class.getModifiers()), "Roles should be final");

        // Constructor should be private
        Constructor<Roles> ctor = Roles.class.getDeclaredConstructor();
        assertTrue(Modifier.isPrivate(ctor.getModifiers()), "Constructor should be private");

        // Ensure reflective access behaves as expected (optional)
        ctor.setAccessible(true);
        Roles instance = ctor.newInstance();
        assertNotNull(instance, "Reflective instantiation should return an instance when accessible");
    }
}
