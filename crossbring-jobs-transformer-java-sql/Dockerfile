# Multi-stage build for Jobs Transformer
FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /build/target/jobs-transformer.jar /app/app.jar

# Config via env
ENV BOOTSTRAP_SERVERS=localhost:9092 \
    TOPIC_JOBS=public.jobs \
    TOPIC_JOB_DETAILS=public.job_details \
    TOPIC_OUT=jobmodel.stg_jobs

ENTRYPOINT ["java","-jar","/app/app.jar"]

