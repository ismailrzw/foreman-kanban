# Architecture Decision Records (ADRs)

> Design decisions, tradeoffs, and architectural rationale for **Foreman Kanban**.

---

## ADR-01: FastAPI + Motor Async Stack Over Flask/Django

- **Status:** Approved
- **Context:** The application requires high concurrency, low memory footprint for free-tier cloud deployment (Render), and native OpenAPI/Pydantic validation for role-based endpoints.
- **Decision:** Use **FastAPI** (Python 3.12) with **Motor** (`AsyncIOMotorClient`).
- **Consequences:**
  - Fast async non-blocking I/O for MongoDB database interactions.
  - Automatic JSON schema generation and parameter validation.
  - Slim memory footprint easily executing within Render's free 512MB RAM cap.

---

## ADR-02: Firebase Authentication + MongoDB Role Binding

- **Status:** Approved
- **Context:** Storing raw passwords or managing custom JWT token refresh logic introduces unnecessary security risks and maintenance overhead.
- **Decision:** Delegate identity management to **Firebase Auth** on the frontend, while managing application roles (`manager` vs `employee`) in MongoDB linked via `firebase_uid`.
- **Consequences:**
  - Zero password storage risk in custom databases.
  - Simple token verification in FastAPI via Firebase Admin SDK.
  - Flexible role management in MongoDB without modifying Firebase user metadata claims.

---

## ADR-03: Bespoke Industrial "Foreman" Design System Over TailwindCSS

- **Status:** Approved
- **Context:** Portfolio standard requires distinct, high-impact aesthetic identity rather than generic UI framework styling.
- **Decision:** Implement a custom Vanilla CSS design system using CSS tokens inspired by physical industrial work order boards (dark panel background `#15130F`, amber accents `#E8A23D`, paper tickets `#FAF6EC`, Oswald/Inter typography, stamp overlay animations).
- **Consequences:**
  - Distinctive, memorable visual aesthetic that sets the project apart.
  - Zero heavy utility CSS dependency overhead.

---

## ADR-04: Multi-Stage Docker Build + Nginx Proxy Strategy

- **Status:** Approved
- **Context:** Frontend Single Page Applications (SPAs) require efficient static asset caching and CORS-avoiding reverse proxying in production containers.
- **Decision:** Build React frontend using Vite in stage 1, then serve static assets using `nginx:1.25-alpine` in stage 2 with built-in API proxy directives.
- **Consequences:**
  - Ultra-small production image sizes (<30MB).
  - High performance static file serving with gzip and 30-day asset caching headers.
