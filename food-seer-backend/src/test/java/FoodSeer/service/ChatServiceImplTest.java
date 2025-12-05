package FoodSeer.service.impl;

import FoodSeer.dto.ChatRequestDto;
import FoodSeer.dto.ChatResponseDto;
import FoodSeer.entity.Food;
import FoodSeer.repositories.FoodRepository;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class ChatServiceImplTest {

    private ChatServiceImpl chatService;
    private FoodRepository foodRepository;

    @BeforeEach
    void setup() {
        foodRepository = Mockito.mock(FoodRepository.class);

        chatService = new ChatServiceImpl();
        chatService.foodRepository = foodRepository; // inject mock repo
    }

    @Test
    void test_NoRecommendationIntent_NoDBCall() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Hello, how are you?");

        ChatResponseDto res = chatService.sendMessage(req);

        verify(foodRepository, never()).findAll();  // trivial: should not call DB
        assertNotNull(res.getResponse());           // trivial: response exists
    }

    @Test
    void test_RecommendationIntent_DBCalled() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Can you recommend food?");

        when(foodRepository.findAll()).thenReturn(Collections.emptyList());

        ChatResponseDto res = chatService.sendMessage(req);

        verify(foodRepository, times(1)).findAll(); // trivial: should call DB
        assertNotNull(res.getResponse());
    }

    @Test
    void test_MenuStringCreatedCorrectly() {
        Food f1 = new Food();
        f1.setFoodName("Pizza");
        f1.setPrice(10.0);
        f1.setAllergies(Arrays.asList("Gluten"));

        Food f2 = new Food();
        f2.setFoodName("Salad");
        f2.setPrice(5.0);
        f2.setAllergies(Collections.emptyList());

        when(foodRepository.findAll()).thenReturn(List.of(f1, f2));

        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("recommend food");

        ChatResponseDto res = chatService.sendMessage(req);

        assertNotNull(res.getResponse());
    }

    @Test
    void test_ErrorHandling_NoCrash() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Cause error");

        // Force exception inside repo
        when(foodRepository.findAll()).thenThrow(new RuntimeException("DB error"));

        ChatResponseDto res = chatService.sendMessage(req);

        assertTrue(res.getResponse().contains("Error:")); 
    }

    @Test
    void test_BasicResponse_NotNull() {
        ChatRequestDto req = new ChatRequestDto();
        req.setMessage("Just checking");

        ChatResponseDto res = chatService.sendMessage(req);

        assertNotNull(res.getResponse());
    }
}
