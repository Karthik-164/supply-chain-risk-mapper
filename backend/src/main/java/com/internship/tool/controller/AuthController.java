package com.internship.tool.controller;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.internship.tool.service.InMemoryUserService;
import com.internship.tool.service.JwtService;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private final InMemoryUserService userService;
    private final JwtService jwtService;

    public AuthController(InMemoryUserService userService, JwtService jwtService) {
        this.userService = userService;
        this.jwtService = jwtService;
    }

    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody AuthRequest request) {
        if (request.username() == null || request.username().isBlank() || request.password() == null || request.password().isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username and password are required"));
        }
        if (!userService.register(request.username(), request.password())) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", "User already exists"));
        }
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "message", "User registered",
                "token", jwtService.generateToken(request.username())));
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody AuthRequest request) {
        if (!userService.authenticate(request.username(), request.password())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid credentials"));
        }
        return ResponseEntity.ok(Map.of(
                "token", jwtService.generateToken(request.username()),
                "username", request.username()));
    }

    @PostMapping("/refresh")
    public ResponseEntity<Map<String, Object>> refresh(@RequestBody RefreshRequest request) {
        if (request.token() == null || !jwtService.isTokenValid(request.token())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid token"));
        }
        String username = jwtService.extractUsername(request.token());
        return ResponseEntity.ok(Map.of("token", jwtService.generateToken(username), "username", username));
    }

    public record AuthRequest(String username, String password) {
    }

    public record RefreshRequest(String token) {
    }
}
