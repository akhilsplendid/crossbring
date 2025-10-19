package com.example.paymentservice.messaging;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Component
public class PaymentListener {
    private static final Logger log = LoggerFactory.getLogger(PaymentListener.class);

    @JmsListener(destination = "payments")
    public void onMessage(String msg) {
        log.info("Received payment message: {}", msg);
    }
}

