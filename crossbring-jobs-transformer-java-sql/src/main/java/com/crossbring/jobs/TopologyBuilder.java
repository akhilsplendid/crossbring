package com.crossbring.jobs;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.JoinWindows;
import org.apache.kafka.streams.kstream.StreamJoined;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Produced;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class TopologyBuilder {

    @Value("${topics.jobs:public.jobs}")
    private String jobsTopic;

    @Value("${topics.jobDetails:public.job_details}")
    private String jobDetailsTopic;

    @Value("${topics.out:jobmodel.stg_jobs}")
    private String outTopic;

    @Bean
    public Topology topology() {
        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> jobs = builder.stream(jobsTopic, Consumed.with(Serdes.String(), Serdes.String()));
        KStream<String, String> details = builder.stream(jobDetailsTopic, Consumed.with(Serdes.String(), Serdes.String()));

        // Simple join by job_id in key; real impl would parse Debezium envelopes
        KStream<String, String> joined = jobs.join(
                details,
                (left, right) -> Json.merge(left, right),
                JoinWindows.ofTimeDifferenceWithNoGrace(java.time.Duration.ofMinutes(30)),
                StreamJoined.with(Serdes.String(), Serdes.String(), Serdes.String())
        );

        // Normalize fields minimally
        KStream<String, String> normalized = joined.mapValues(Json::normalizeJob);
        normalized.to(outTopic, Produced.with(Serdes.String(), Serdes.String()));

        return builder.build();
    }

    public static java.util.Properties streamsConfig(String appName) {
        java.util.Properties props = new java.util.Properties();
        props.put("application.id", appName);
        props.put("bootstrap.servers", System.getProperty("bootstrap.servers", System.getenv().getOrDefault("BOOTSTRAP_SERVERS", "localhost:9092")));
        props.put("default.key.serde", Serdes.String().getClass());
        props.put("default.value.serde", Serdes.String().getClass());
        return props;
    }

    // Tiny JSON helper for demo purposes
    static class Json {
        static String merge(String a, String b) {
            Map<String, Object> ma = parse(a);
            Map<String, Object> mb = parse(b);
            if (ma == null) return b; if (mb == null) return a;
            ma.putAll(mb);
            return toJson(ma);
        }
        static String normalizeJob(String merged) {
            Map<String, Object> m = parse(merged);
            if (m == null) return merged;
            // Example normalization
            m.put("city", str(m.get("city")).trim());
            m.put("region", str(m.get("region")).trim());
            m.put("title", str(m.get("title")));
            return toJson(m);
        }
        static Map<String, Object> parse(String json) {
            try {
                return new com.fasterxml.jackson.databind.ObjectMapper().readValue(json, Map.class);
            } catch (Exception e) { return null; }
        }
        static String toJson(Map<String, Object> m) {
            try {
                return new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(m);
            } catch (Exception e) { return "{}"; }
        }
        static String str(Object o) { return o == null ? "" : String.valueOf(o); }
    }
}
