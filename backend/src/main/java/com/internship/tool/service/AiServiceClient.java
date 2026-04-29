package com.internship.tool.service;

import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

@Service
public class AiServiceClient {

    private static final Logger logger = LoggerFactory.getLogger(AiServiceClient.class);

    private final RestTemplate restTemplate;
    private final String aiServiceBaseUrl;

    public AiServiceClient(
            RestTemplate restTemplate,
            @Value("${ai.service.base-url:http://localhost:5000}") String aiServiceBaseUrl) {
        this.restTemplate = restTemplate;
        this.aiServiceBaseUrl = aiServiceBaseUrl;
    }

    public Map<String, Object> describe(Map<String, Object> request) {
        return postForMap("/describe", request);
    }

    public List<Map<String, Object>> recommend(Map<String, Object> request) {
        try {
            ResponseEntity<List<Map<String, Object>>> response = restTemplate.exchange(
                    buildUrl("/recommend"),
                    HttpMethod.POST,
                    new HttpEntity<>(request),
                    new ParameterizedTypeReference<>() {
                    });
            return response.getBody();
        } catch (RestClientException ex) {
            logger.warn("AI recommend request failed", ex);
            return null;
        }
    }

    public Map<String, Object> generateReport(Map<String, Object> request) {
        return postForMap("/generate-report", request);
    }

    public Map<String, Object> health() {
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    buildUrl("/health"),
                    HttpMethod.GET,
                    HttpEntity.EMPTY,
                    new ParameterizedTypeReference<>() {
                    });
            return response.getBody();
        } catch (RestClientException ex) {
            logger.warn("AI health request failed", ex);
            return null;
        }
    }

    private Map<String, Object> postForMap(String path, Map<String, Object> request) {
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    buildUrl(path),
                    HttpMethod.POST,
                    new HttpEntity<>(request),
                    new ParameterizedTypeReference<>() {
                    });
            return response.getBody();
        } catch (RestClientException ex) {
            logger.warn("AI request to {} failed", path, ex);
            return null;
        }
    }

    private String buildUrl(String path) {
        if (path.startsWith("/")) {
            return aiServiceBaseUrl + path;
        }
        return aiServiceBaseUrl + "/" + path;
    }
}
