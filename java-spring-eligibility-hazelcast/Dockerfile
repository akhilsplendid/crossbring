FROM gradle:8.10.2-jdk21-alpine AS build
WORKDIR /app
COPY . .
RUN gradle bootJar --no-daemon

FROM eclipse-temurin:21-jre-alpine
ENV JVM_OPTS="-XX:InitialRAMPercentage=50 -XX:MaxRAMPercentage=80"
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8083
ENTRYPOINT ["sh","-c","java $JVM_OPTS -jar app.jar"]
