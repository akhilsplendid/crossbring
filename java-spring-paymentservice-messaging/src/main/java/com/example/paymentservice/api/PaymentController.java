 package com.example.paymentservice.api;

import jakarta.jms.JMSException;
import org.springframework.http.ResponseEntity;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    private final JmsTemplate jmsTemplate;

    public PaymentController(JmsTemplate jmsTemplate) {
        this.jmsTemplate = jmsTemplate;
    }

    @PostMapping
    public ResponseEntity<?> publish(@RequestBody Map<String, Object> payload) throws JMSException {
        jmsTemplate.convertAndSend("payments", payload);
        return ResponseEntity.accepted().body(Map.of("status", "QUEUED"));
    }
}

