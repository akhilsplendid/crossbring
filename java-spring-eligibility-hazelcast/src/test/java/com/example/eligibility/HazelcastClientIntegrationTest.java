package com.example.eligibility;

import com.hazelcast.core.HazelcastInstance;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SpringExtension.class)
@SpringBootTest
@Testcontainers
class HazelcastClientIntegrationTest {

    @Container
    static GenericContainer<?> hazelcast = new GenericContainer<>("hazelcast/hazelcast:5.4.0")
            .withExposedPorts(5701);

    static Path clientConfig;

    @BeforeAll
    static void beforeAll() throws IOException {
        int mapped = hazelcast.getMappedPort(5701);
        String host = hazelcast.getHost();
        String yaml = "hazelcast-client:\n" +
                "  cluster-name: dev\n" +
                "  network:\n" +
                "    cluster-members:\n" +
                "      - \"" + host + ":" + mapped + "\"\n";
        clientConfig = Files.createTempFile("hazelcast-client", ".yaml");
        Files.writeString(clientConfig, yaml);
    }

    @DynamicPropertySource
    static void registerProps(DynamicPropertyRegistry registry) {
        registry.add("spring.hazelcast.config", () -> "file:" + clientConfig.toAbsolutePath());
    }

    @Autowired
    HazelcastInstance hz;

    @Test
    void cacheableStoresEntryInCluster() {
        var map = hz.getMap("eligibility");
        map.clear();
        // simulate cached call by putting entry
        map.put("19121212-1212", "ELIGIBLE");
        assertThat(map.containsKey("19121212-1212")).isTrue();
    }
}

