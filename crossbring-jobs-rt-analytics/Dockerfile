# Multi-stage build for Jobs Real-time Analytics
FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /build/target/jobs-rt-analytics.jar /app/app.jar

ENV BOOTSTRAP_SERVERS=localhost:9092 \
    TOPIC_IN=jobmodel.stg_jobs

ENTRYPOINT ["java","-jar","/app/app.jar"]

