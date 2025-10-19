package com.example.paymentservice;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SpringExtension.class)
@SpringBootTest
@Testcontainers
class JmsIntegrationTest {

    @Container
    static GenericContainer<?> artemis = new GenericContainer<>("vromero/activemq-artemis:2.31.2")
            .withEnv("ARTEMIS_USERNAME", "artemis")
            .withEnv("ARTEMIS_PASSWORD", "artemis")
            .withExposedPorts(61616, 8161);

    @DynamicPropertySource
    static void registerProps(DynamicPropertyRegistry registry) {
        registry.add("spring.artemis.host", () -> artemis.getHost());
        registry.add("spring.artemis.port", () -> artemis.getMappedPort(61616));
        registry.add("spring.artemis.user", () -> "artemis");
        registry.add("spring.artemis.password", () -> "artemis");
    }

    @Autowired
    JmsTemplate jmsTemplate;

    @Test
    void sendAndReceive_onTestQueue() {
        Assumptions.assumeTrue("true".equalsIgnoreCase(System.getenv("ENABLE_TESTCONTAINERS")),
                "Skipping JMS Testcontainers test unless ENABLE_TESTCONTAINERS=true");
        jmsTemplate.convertAndSend("test-queue", "hello");
        jmsTemplate.setReceiveTimeout(2000);
        Object msg = jmsTemplate.receiveAndConvert("test-queue");
        assertThat(msg).isEqualTo("hello");
    }
}
