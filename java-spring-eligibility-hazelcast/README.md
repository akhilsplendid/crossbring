java-spring-eligibility-hazelcast
Purpose: Demonstrates Spring Boot caching with Hazelcast.

Highlights
- Java 21 + Spring Boot + Hazelcast
- Endpoint: GET /api/eligibility/{pnr} with @Cacheable
- Dockerfile, K8s manifests, Helm chart

Run locally
- `gradle bootRun`
- Call: `curl localhost:8083/api/eligibility/19121212-1212`

Next steps
- Externalize Hazelcast cluster to K8s, add management center.
