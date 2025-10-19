Crossbring Jobs Transformer (Java + SQL)

Purpose
- Transform raw CDC events (`public.jobs`, `public.job_details`) into the normalized `jobmodel` schema with idempotent upserts and late-arrival handling.

Build
- Requires Java 21 and Maven 3.9+.
- `mvn -q -DskipTests package`

Run (example)
- `java -jar target/jobs-transformer.jar`
- Configure via `src/main/resources/application.properties` (Kafka, Postgres DSN).

