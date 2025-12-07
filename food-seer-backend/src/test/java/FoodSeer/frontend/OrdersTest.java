package FoodSeer.frontend;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.File;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.Alert;
import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.support.ui.Select;
import java.util.List;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import io.github.bonigarcia.wdm.WebDriverManager;

public class OrdersTest {

    private ChromeDriver driver;

    @BeforeEach
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        driver = new ChromeDriver(options);
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void testDefaultRatingValueAndSubmit() throws Exception {
        // Load the local mock HTML page
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        // Ensure select exists and default value is 5
        WebElement select = driver.findElement(By.id("rating-select-100"));
        assertEquals("5", select.getAttribute("value"));

        // Click the Rate button and accept the alert
        WebElement rateBtn = driver.findElement(By.id("rate-btn-100"));
        rateBtn.click();

        Alert alert = driver.switchTo().alert();
        assertTrue(alert.getText().toLowerCase().contains("rating submitted"));
        alert.accept();

        // After accepting, the button should be disabled and show Rated
        WebElement afterBtn = driver.findElement(By.id("rate-btn-100"));
        assertTrue(afterBtn.getAttribute("disabled") != null || !afterBtn.isEnabled());
        assertTrue(afterBtn.getText().contains("Rated"));
    }

    @Test
    public void testChangeRatingThenSubmit() throws Exception {
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        WebElement select = driver.findElement(By.id("rating-select-100"));
        // Change to 3
        select.sendKeys("3");
        assertEquals("3", select.getAttribute("value"));

        WebElement rateBtn = driver.findElement(By.id("rate-btn-100"));
        rateBtn.click();

        Alert alert = driver.switchTo().alert();
        alert.accept();

        WebElement afterBtn = driver.findElement(By.id("rate-btn-100"));
        assertTrue(afterBtn.getText().contains("Rated"));
    }

    @Test
    public void testOrderCardAndFoodPresence() throws Exception {
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        // Ensure order card exists
        WebElement orderCard = driver.findElement(By.id("order-1"));
        assertTrue(orderCard.isDisplayed());

        // Ensure food item row exists and has expected food name
        WebElement foodRow = driver.findElement(By.id("food-100"));
        WebElement foodName = foodRow.findElement(By.className("food-name"));
        assertEquals("Test Food", foodName.getText());
    }

    @Test
    public void testSelectOptionsCountAndTexts() throws Exception {
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        WebElement select = driver.findElement(By.id("rating-select-100"));
        // There should be 5 options (5,4,3,2,1)
        int optionsCount = select.findElements(By.tagName("option")).size();
        assertEquals(5, optionsCount);

        // First option text should contain '5'
        String firstText = select.findElements(By.tagName("option")).get(0).getText();
        assertTrue(firstText.startsWith("5"));
    }

    @Test
    public void testAllOptionValuesSelectable() throws Exception {
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        Select sel = new Select(driver.findElement(By.id("rating-select-100")));
        List<WebElement> options = sel.getOptions();
        for (WebElement opt : options) {
            String val = opt.getAttribute("value");
            sel.selectByValue(val);
            assertEquals(val, sel.getFirstSelectedOption().getAttribute("value"));
        }
    }

    @Test
    public void testRateDisablesThenRefreshReenables() throws Exception {
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        WebElement rateBtn = driver.findElement(By.id("rate-btn-100"));
        rateBtn.click();
        Alert alert = driver.switchTo().alert();
        alert.accept();

        WebElement afterBtn = driver.findElement(By.id("rate-btn-100"));
        assertTrue(afterBtn.getAttribute("disabled") != null || !afterBtn.isEnabled());

        // Refresh page: mock resets, so button should be enabled again
        driver.navigate().refresh();
        WebElement btnAfterRefresh = driver.findElement(By.id("rate-btn-100"));
        assertTrue(btnAfterRefresh.isEnabled());
    }

    @Test
    public void testSecondClickDoesNotShowAlert() throws Exception {
        File mock = new File("src/test/resources/mock-pages/orders-mock.html");
        String url = mock.getAbsoluteFile().toURI().toString();
        driver.get(url);

        WebElement rateBtn = driver.findElement(By.id("rate-btn-100"));
        rateBtn.click();
        Alert alert = driver.switchTo().alert();
        alert.accept();

        // Button now disabled -- clicking should have no effect
        WebElement afterBtn = driver.findElement(By.id("rate-btn-100"));
        try {
            afterBtn.click();
        } catch (Exception ignored) {
            // clicking a disabled button may throw; ignore
        }

        // Ensure no alert is present
        boolean alertPresent = true;
        try {
            driver.switchTo().alert();
        } catch (NoAlertPresentException ex) {
            alertPresent = false;
        }
        assertTrue(!alertPresent);
    }
}
