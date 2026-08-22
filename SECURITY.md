# Security Policy

## Supported Versions

We issue security updates for the latest stable release of **Foreman Kanban**.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of **Foreman Kanban** seriously. If you believe you have found a security vulnerability in this project, please report it to us responsibly.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security issues by:
1. Opening a [Private Security Advisory](https://github.com/sedmugen/foreman-kanban/security/advisories/new) on GitHub, or
2. Contacting the lead maintainer directly via email at `security@foreman.dev`.

### What to Include in Your Report

To help us triage and resolve the issue quickly, please include:
- A description of the vulnerability and its potential impact.
- Step-by-step instructions to reproduce the issue (including proof-of-concept code or HTTP requests if applicable).
- Affected components (Frontend, Backend REST API, Database, or Infrastructure).

### Response Timeline

- **Initial Acknowledgment:** Within 48 hours.
- **Triage & Assessment:** Within 5 business days.
- **Fix & Patch Release:** Target within 14 business days depending on severity.

For details on the project's security architecture, Firebase JWT verification, and server-side RBAC guards, please refer to [docs/security.md](docs/security.md).
