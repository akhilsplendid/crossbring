package com.crossbring.jobs;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.kstream.Windowed;
import org.apache.kafka.streams.kstream.Grouped;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.Topology;

import java.time.Duration;

public class RealtimeAnalyticsApp {
    public static void main(String[] args) {
        StreamsBuilder b = new StreamsBuilder();
        String topic = System.getenv().getOrDefault("TOPIC_IN", "jobmodel.stg_jobs");
        KStream<String, String> in = b.stream(topic, Consumed.with(Serdes.String(), Serdes.String()));

        var regionCounts = in
            .map((k, v) -> KeyValue.pair(Json.get(v, "region"), 1L))
            .groupByKey(Grouped.with(Serdes.String(), Serdes.Long()))
            .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(24)))
            .count(Materialized.as("region-counts"));

        Topology topology = b.build();
        KafkaStreams streams = new KafkaStreams(topology, Config.props("jobs-rt-analytics"));
        streams.start();
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }

    static class Config {
        static java.util.Properties props(String appId) {
            var p = new java.util.Properties();
            p.put("application.id", appId);
            p.put("bootstrap.servers", System.getenv().getOrDefault("BOOTSTRAP_SERVERS", "localhost:9092"));
            return p;
        }
    }

    static class Json {
        static String get(String json, String field) {
            try {
                var m = new com.fasterxml.jackson.databind.ObjectMapper().readTree(json);
                var n = m.get(field);
                return n == null ? "" : n.asText();
            } catch (Exception e) { return ""; }
        }
    }
}

