package FoodSeer.frontend;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;

import FoodSeer.service.impl.DataInitializer;
import io.github.bonigarcia.wdm.WebDriverManager;
import jakarta.transaction.Transactional;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
@Transactional
@AutoConfigureMockMvc
public class LoginPageTest {

    private ChromeDriver driver;

    // URL for our driver to start at
    private String baseUrl = "http://localhost:3000/";

    private String adminUsername = "admin";

    // Wait object to handle time outs
    private WebDriverWait wait;

    @Value("${app.admin-user-password}")
    private String adminPassword;

    // Puts our admin in our repository
    @Autowired
    private DataInitializer dataInitializer;

    // Sets up the chrome driver and the wait object
    @BeforeEach
    public void setUp() {
        dataInitializer.onApplicationReady();
        WebDriverManager.chromedriver().setup();

        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new");
        options.addArguments("--disable-gpu");
        options.addArguments("--window-size=1920,1080");
        options.addArguments("--disable-extensions");
        options.addArguments("--disable-software-rasterizer");
        driver = new ChromeDriver(options);

        wait = new WebDriverWait(driver, java.time.Duration.ofSeconds(20));
    }

    // Closes the web driver
    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    /**
     * Tests the admin user logging in
     * Verifies that:
     * - Admin should be initialized in the system
     * - Upon logging in, the admin is directed to order-management
     */
    @Test
    public void testAdminLogin() {
        attemptLogin(adminUsername, adminPassword);

        // Assert login is successful by checking we make it to the order management page
        wait.until(d -> d.getCurrentUrl().equals("http://localhost:3000/order-management"));
        assertEquals(driver.getCurrentUrl(), "http://localhost:3000/order-management");
    }

    /**
     * Tests a login for a user that doesn't exist
     * Verifies that:
     * - There should be no redirect on unsuccessful login
     * - An error message should appear when giving improper credentials
     */
    @Test
    public void testInvalidLogin() {
        attemptLogin("WrongUser", "WrongPass");

        // Assert login failed by checking we are still on the login page
        wait.until(d -> d.getCurrentUrl().equals("http://localhost:3000/"));
        assertEquals(driver.getCurrentUrl(), baseUrl);
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("error-message")));
        assertEquals(driver.findElement(By.className("error-message")).getText(), "Invalid username or password");
    }

    /**
     * Tests that empty credentials are not submitted to the form
     * Verifies that:
     * - There are no error messages on empty fields
     * - No redirect when form doesn't submit
     */
    @Test
    public void testEmptyCredentials() {
        attemptLogin("", "");

        // Assert login failed by checking we are still on the login page
        wait.until(d -> d.getCurrentUrl().equals("http://localhost:3000/"));
        assertEquals(driver.getCurrentUrl(), baseUrl);
        assertThrows(Exception.class, () -> {driver.findElement(By.id("error-message"));});
    }

    /**
     * Tests that partial credentials still do not allow form submission
     * Verifies that:
     * - Entering nothing into the password or username fields individually causes no submission
     * - There are no errors for empty fields
     */
    @Test
    public void testPartialCredentials() {
        attemptLogin(adminUsername, "");

        // Assert login failed by checking we are still on the login page
        assertEquals(driver.getCurrentUrl(), baseUrl);
        // assertEquals(driver.findElement(By.id("error-message")).getText(), "Username and password cannot be empty");

        attemptLogin("", adminPassword);

        // Assert login failed by checking we are still on the login page
        assertEquals(driver.getCurrentUrl(), baseUrl);
        assertThrows(Exception.class, () -> {driver.findElement(By.id("error-message"));});
    }

    /**
     * Tests that the register link exists and take the user to the registration page
     * Verifies that
     * - A registration link exists
     * - It takes the user to the correct page
     */
    @Test
    public void testRegisterLink(){
        driver.get(baseUrl);

        // Click the register link
        var registerLink = driver.findElement(By.cssSelector("a[href='/register']"));
        registerLink.click();

        // Assert we are on the registration page
        wait.until(d -> d.getCurrentUrl().equals("http://localhost:3000/register"));
        assertEquals(driver.getCurrentUrl(), "http://localhost:3000/register");
    }

    private void attemptLogin(String username, String password) {
        driver.get(baseUrl);
        wait.until(ExpectedConditions.elementToBeClickable(By.className("login-button")));

        System.out.println("Loaded page title: " + driver.getTitle());
        System.out.println("Current URL: " + driver.getCurrentUrl());

        // Find username and password fields and login button
        var usernameField = driver.findElement(By.id("username"));
        var passwordField = driver.findElement(By.id("password"));
        var loginButton = driver.findElement(By.className("login-button"));

        // Enter credentials
        usernameField.sendKeys(username);
        passwordField.sendKeys(password);

        // Click login button

        loginButton.click();
    }
}
