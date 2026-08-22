# Changelog

All notable changes to the **Foreman Kanban** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-05

### Added
- Portfolio standardization refactoring following `PORTFOLIO-STANDARDS.md`.
- Comprehensive backend pytest suite (`test_auth.py`, `test_tasks.py`, `test_health.py`).
- Architecture documentation (`docs/architecture.md`, `docs/api.md`, `docs/decisions.md`).
- SVG architecture & state machine workflow diagrams in `assets/images/`.
- MIT License, `CONTRIBUTING.md`, and `CHANGELOG.md`.

### Refactored
- `InspectionQueue.jsx` component to reuse `RejectPanel.jsx` component.
- Cleaned up residual comments and unused Vite template assets.
- Restructured `README.md` into a visual-first portfolio showcase with original lab spec archived to `docs/coursework-spec.md`.

### Core Features
- Role-Based Access Control (RBAC) for Managers and Employees.
- Task status state machine with PR review/merge metaphor.
- Firebase Authentication with FastAPI Admin SDK verification.
- MongoDB Atlas document persistence via Motor driver.
- Multi-stage Docker containers, Docker Compose, and minikube K8s manifests.
- GitHub Actions CI/CD workflows for automated linting, testing, and cloud deployment.
