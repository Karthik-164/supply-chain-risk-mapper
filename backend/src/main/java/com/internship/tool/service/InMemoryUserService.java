package com.internship.tool.service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class InMemoryUserService {

    private final Map<String, String> users = new ConcurrentHashMap<>();
    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public InMemoryUserService() {
        users.put("demo", passwordEncoder.encode("demo123"));
    }

    public boolean register(String username, String password) {
        if (users.containsKey(username)) {
            return false;
        }
        users.put(username, passwordEncoder.encode(password));
        return true;
    }

    public boolean authenticate(String username, String password) {
        String hashedPassword = users.get(username);
        return hashedPassword != null && passwordEncoder.matches(password, hashedPassword);
    }

    public boolean exists(String username) {
        return users.containsKey(username);
    }
}
