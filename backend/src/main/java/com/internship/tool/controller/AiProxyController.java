package com.internship.tool.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.internship.tool.service.AiServiceClient;

@RestController
@RequestMapping
public class AiProxyController {

    private final AiServiceClient aiServiceClient;

    public AiProxyController(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    @GetMapping("/public/health")
    public Map<String, String> publicHealth() {
        return Map.of("status", "ok");
    }

    @GetMapping("/api/ai/health")
    public ResponseEntity<?> aiHealth() {
        Map<String, Object> response = aiServiceClient.health();
        if (response == null) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of("error", "AI service unavailable"));
        }
        return ResponseEntity.ok(response);
    }

    @PostMapping("/api/ai/describe")
    public ResponseEntity<?> describe(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = aiServiceClient.describe(request);
        if (response == null) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of("error", "AI service unavailable"));
        }
        return ResponseEntity.ok(response);
    }

    @PostMapping("/api/ai/recommend")
    public ResponseEntity<?> recommend(@RequestBody Map<String, Object> request) {
        List<Map<String, Object>> response = aiServiceClient.recommend(request);
        if (response == null) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of("error", "AI service unavailable"));
        }
        return ResponseEntity.ok(response);
    }

    @PostMapping("/api/ai/generate-report")
    public ResponseEntity<?> generateReport(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = aiServiceClient.generateReport(request);
        if (response == null) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of("error", "AI service unavailable"));
        }
        return ResponseEntity.ok(response);
    }
}
