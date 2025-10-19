java-spring-paymentservice-messaging
Purpose: Demonstrates JMS messaging with ActiveMQ Artemis using Spring Boot.

Highlights
- Java 21 + Spring Boot Artemis starter (JMS)
- REST endpoint to publish a payment message; JMS listener consumes from queue
- Dockerfile, K8s manifests, Helm chart
- docker-compose for local Artemis broker

Run locally
- Start broker: `docker compose up -d`
- App: `gradle bootRun`
- Send message: `curl -X POST localhost:8082/api/payments -H "Content-Type: application/json" -d '{"amount":100,"currency":"SEK"}'`

Config
- Env vars: `ARTEMIS_HOST`, `ARTEMIS_PORT`, `ARTEMIS_USER`, `ARTEMIS_PASSWORD` (see application.yml)
