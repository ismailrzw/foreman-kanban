# Contributing Guidelines

Thank you for your interest in contributing to **Foreman Kanban**!

---

## 1. Branch Naming Conventions

All branches must use the following format:

```
<category>/<short-description>
```

Approved categories:
- `feature/` — New features or feature extensions
- `bugfix/` — Bug fixes
- `hotfix/` — Urgent production fixes
- `docs/` — Documentation updates
- `refactor/` — Code refactoring without behavioral changes
- `test/` — Adding or updating test cases
- `chore/` — Build system, CI/CD, or maintenance updates

Examples: `feature/add-activity-log`, `refactor/portfolio-standardization`, `docs/update-api-spec`.

---

## 2. Conventional Commit Messages

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(optional-scope): description
```

Approved types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `build`, `ci`.

Rules:
- Write in the imperative mood (e.g. `feat: add task filtering by complexity`).
- Keep the first line under 72 characters.
- Never use generic commit messages like `Update`, `Fix`, `Changes`, or `asdf`.

---

## 3. Pull Request Process

1. Create your feature/fix branch from `develop`.
2. Ensure code passes all linters (`ruff check app/` in backend, `eslint` in frontend).
3. Ensure all automated tests pass (`python -m pytest tests/` in backend).
4. Submit a Pull Request targeting the `develop` branch using the repository PR template.
5. Code must receive review approval before merging to `main`.
