// java
package FoodSeer.service;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import FoodSeer.repositories.FoodRepository;
import FoodSeer.repositories.RoleRepository;
import FoodSeer.repositories.UserRepository;
import FoodSeer.service.impl.DataInitializer;

@SpringBootTest
@Transactional
public class DataInitializerTest {

    @Autowired
    private DataInitializer dataInitializer;

    @Autowired
    private FoodRepository foodRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RoleRepository roleRepository;

    @BeforeEach
    public void setup() {
//        foodRepository.deleteAll();
//        userRepository.deleteAll();
//        roleRepository.deleteAll();
    }

//    @Test
//    @Transactional
//    public void testAdminUserAndRolesCreated() {
//        assertEquals(0, userRepository.count());
//        assertEquals(0, roleRepository.count());
//
//        dataInitializer.onApplicationReady();
//
//        // roles should exist
//        assertNotNull(roleRepository.findByName("ROLE_ADMIN"));
//        assertNotNull(roleRepository.findByName("ROLE_CUSTOMER"));
//        assertNotNull(roleRepository.findByName("ROLE_STAFF"));
//
//        // admin user should be created
//        assertTrue(userRepository.findByUsername("admin").isPresent());
//    }
//
//    @Test
//    @Transactional
//    public void testAdminPasswordNotChangedIfAdminExists() {
//        // Run initializer once to create admin
//        dataInitializer.onApplicationReady();
//        String originalHash = userRepository.findByUsername("admin").get().getPassword();
//
//        // Run initializer again — should NOT update existing admin password
//        dataInitializer.onApplicationReady();
//        String afterHash = userRepository.findByUsername("admin").get().getPassword();
//
//        // password hashes should match (no update)
//        assertEquals(originalHash, afterHash);
//    }
//
//    @Test
//    @Transactional
//    public void testSampleFoodsCreatedWhenEmpty() {
//        assertEquals(0, foodRepository.count());
//
//        dataInitializer.onApplicationReady();
//
//        assertTrue(foodRepository.count() > 0,
//                "Expected sample foods to be seeded");
//    }

    @Test
    @Transactional
    public void testSampleFoodsNotDuplicatedOnSecondRun() {
        dataInitializer.onApplicationReady();
        long firstCount = foodRepository.count();

        dataInitializer.onApplicationReady();
        long secondCount = foodRepository.count();

        assertEquals(firstCount, secondCount,
                "Food seeding should NOT repeat");
    }
}
