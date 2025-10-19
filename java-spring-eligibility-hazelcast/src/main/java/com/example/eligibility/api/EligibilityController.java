package com.example.eligibility.api;

import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api/eligibility")
public class EligibilityController {

    @GetMapping("/{pnr}")
    @Cacheable("eligibility")
    public ResponseEntity<Map<String, Object>> eligibility(@PathVariable String pnr) throws InterruptedException {
        // Simulate expensive computation
        Thread.sleep(500);
        return ResponseEntity.ok(Map.of(
                "pnr", pnr,
                "eligible", Boolean.TRUE,
                "computedAt", Instant.now().toString()
        ));
    }
}

