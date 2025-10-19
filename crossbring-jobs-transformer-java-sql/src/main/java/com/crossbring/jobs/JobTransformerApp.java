package com.crossbring.jobs;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.Topology;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class JobTransformerApp {

    public static void main(String[] args) {
        SpringApplication.run(JobTransformerApp.class, args);
    }

    @Bean
    public CommandLineRunner run(Topology topology,
                                 @Value("${spring.application.name:jobs-transformer}") String appName) {
        return args -> {
            KafkaStreams streams = new KafkaStreams(topology, TopologyBuilder.streamsConfig(appName));
            streams.start();
            Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
        };
    }
}

