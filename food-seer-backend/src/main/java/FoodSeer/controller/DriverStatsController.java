package FoodSeer.controller;

import FoodSeer.dto.DriverStatsDto;
import FoodSeer.exception.ResourceNotFoundException;
import FoodSeer.service.DriverStatsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.parameters.P;
import org.springframework.web.bind.annotation.*;

@CrossOrigin("*")
@RestController
@RequestMapping("/api/driverStats")
public class DriverStatsController {

    @Autowired
    DriverStatsService driverStatsService;

    @GetMapping
    @PreAuthorize("hasRole('ADMIN') or (hasRole('DRIVER') and @driverStatsAccess.isOwner(authentication, #username))")
    public ResponseEntity<?> getDriverStats(@P("username") @RequestParam("username") String username) {

        DriverStatsDto driverStatsDto = driverStatsService.getDriverStats(username);
        if (driverStatsDto == null) {
            throw new ResourceNotFoundException("Driver statistics not found");
        }
        return ResponseEntity.ok().body(driverStatsDto);
    }
}
