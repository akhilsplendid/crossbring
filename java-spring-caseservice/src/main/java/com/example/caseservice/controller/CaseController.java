package com.example.caseservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api/cases")
public class CaseController {

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getCase(@PathVariable String id) {
        return ResponseEntity.ok(Map.of(
                "id", id,
                "status", "OPEN",
                "assignedTo", "system",
                "updatedAt", Instant.now().toString()
        ));
    }
}

