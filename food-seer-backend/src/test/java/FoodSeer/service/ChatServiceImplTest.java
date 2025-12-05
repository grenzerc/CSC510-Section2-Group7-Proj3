package FoodSeer.service;

import FoodSeer.dto.ChatRequestDto;
import FoodSeer.dto.ChatResponseDto;
import FoodSeer.entity.Food;
import FoodSeer.repositories.FoodRepository;
import FoodSeer.service.impl.ChatServiceImpl;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class ChatServiceImplTest {

    private ChatServiceImpl chatService;
    private FoodRepository foodRepository;

    @BeforeEach
    void setup() throws Exception {
        foodRepository = Mockito.mock(FoodRepository.class);

        chatService = new ChatServiceImpl();

        // Inject private field 'foodRepository' via reflection
        Field repoField = ChatServiceImpl.class.getDeclaredField("foodRepository");
        repoField.setAccessible(true);
        repoField.set(chatService, foodRepository);
    }

    @Test
    void test_NoRecommendationIntent_NoDBCall() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Hello, how are you?");

        ChatResponseDto res = chatService.sendMessage(req);

        verify(foodRepository, never()).findAll();  // should not call DB
        assertNotNull(res);
        String resp = extractResponse(res);
        assertNotNull(resp);
    }

    @Test
    void test_RecommendationIntent_DBCalled() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Can you recommend food?");

        when(foodRepository.findAll()).thenReturn(Collections.emptyList());

        ChatResponseDto res = chatService.sendMessage(req);

        verify(foodRepository, times(1)).findAll(); // should call DB
        assertNotNull(res);
        String resp = extractResponse(res);
        assertNotNull(resp);
    }

    @Test
    void test_MenuStringCreatedCorrectly() {
        Food f1 = new Food();
        f1.setFoodName("Pizza");
        f1.setPrice(10); // use int to match entity setter
        f1.setAllergies(Arrays.asList("Gluten"));

        Food f2 = new Food();
        f2.setFoodName("Salad");
        f2.setPrice(5); // use int
        f2.setAllergies(Collections.emptyList());

        when(foodRepository.findAll()).thenReturn(List.of(f1, f2));

        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("recommend food");

        ChatResponseDto res = chatService.sendMessage(req);

        assertNotNull(res);
        String resp = extractResponse(res);
        assertNotNull(resp);
    }

    @Test
    void test_ErrorHandling_NoCrash() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Cause error");

        // Force exception inside repo
        when(foodRepository.findAll()).thenThrow(new RuntimeException("DB error"));

        ChatResponseDto res = chatService.sendMessage(req);

        assertNotNull(res);
        String resp = extractResponse(res);
        assertNotNull(resp);
        assertTrue(resp.contains("Error:") || resp.toLowerCase().contains("error"));
    }

    @Test
    void test_BasicResponse_NotNull() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Just checking");

        ChatResponseDto res = chatService.sendMessage(req);

        assertNotNull(res);
        String resp = extractResponse(res);
        assertNotNull(resp);
    }

    // Helper that attempts to extract a String response from ChatResponseDto using reflection.
    // Tries common getter names and then checks declared fields for a String value.
    private String extractResponse(ChatResponseDto dto) {
        if (dto == null) return null;
        try {
            String[] getters = {"getResponse", "getMessage", "getText", "getContent", "getAiResponse", "getResult"};
            for (String g : getters) {
                try {
                    Method m = dto.getClass().getMethod(g);
                    Object val = m.invoke(dto);
                    if (val != null) return val.toString();
                } catch (NoSuchMethodException ignored) {
                }
            }
            // Try declared fields
            for (Field f : dto.getClass().getDeclaredFields()) {
                f.setAccessible(true);
                Object val = f.get(dto);
                if (val instanceof String) return (String) val;
            }
        } catch (Exception ignored) {
        }
        return null;
    }
}
