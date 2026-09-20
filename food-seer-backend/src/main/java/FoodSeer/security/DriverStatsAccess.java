package FoodSeer.security;

import FoodSeer.repositories.UserRepository;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

/** Resolves ownership without assuming the login identifier is a username. */
@Component("driverStatsAccess")
public class DriverStatsAccess {
    private final UserRepository users;

    public DriverStatsAccess(UserRepository users) {
        this.users = users;
    }

    public boolean isOwner(Authentication authentication, String username) {
        String login = authentication.getName();
        return users.findByUsernameOrEmail(login, login)
                .map(user -> user.getUsername().equals(username))
                .orElse(false);
    }
}
