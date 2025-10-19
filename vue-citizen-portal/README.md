vue-citizen-portal
Purpose: Vue 3 + Vite frontend to interact with backend services.

Highlights
- Vue 3, Vite, Axios
- Simple UI calls caseservice and eligibility endpoints
- Dockerfile for production build with Nginx
- K8s manifests + Helm chart

Dev
- `npm install`
- `npm run dev` -> http://localhost:5173

Build & Run (Docker)
- `docker build -t citizen-portal:dev . && docker run -p 8080:80 citizen-portal:dev`
