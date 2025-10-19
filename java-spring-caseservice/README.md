java-spring-caseservice
Purpose: Spring Boot REST microservice (Gradle) with Docker, K8s, Helm, and ArgoCD template.

Highlights
- Java 21 + Spring Boot Web
- REST endpoint: GET /api/cases/{id}
- Gradle build, Dockerfile
- K8s manifests + Helm chart skeleton
- ArgoCD Application template (GitOps-ready)

Run locally
- Java: `gradle bootRun`
- Docker: `docker build -t caseservice:dev . && docker run -p 8081:8081 caseservice:dev`

Kubernetes (example)
- `helm upgrade --install caseservice ./helm/caseservice -n cases --create-namespace --set image.repository=your-registry/caseservice,image.tag=dev`

ArgoCD
- Use `argo/app-caseservice.yaml` and set your Git repo URL/paths.

Next steps
- Add persistence and domain validations.
- Add Actuator and metrics.
