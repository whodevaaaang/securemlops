# Architecture

## System diagram

```mermaid
flowchart LR
    Dev[Developer] -->|git push| Repo[(GitHub Repo)]
    Repo -->|trigger| GA[GitHub Actions]

    subgraph Pipeline
        direction TB
        B[Build & Lint] --> T[Test + Security Scan]
        T --> D[Build Image + Trivy Scan]
        D --> Dep[Deploy Container]
    end

    GA --> Pipeline
    Dep -->|docker run| Container[(SecureMLOps API :8000)]
    Container -->|/predict, /health| User[End User / Smoke Test]

    Secrets[(GitHub Secrets)] -.injects API_TOKEN.-> Dep
```

## Pipeline stages

| Stage | Job | Gate |
|------|-----|------|
| 1 | Build & Lint | flake8, black, model train |
| 2 | Test & Security | pytest + coverage, Bandit, Gitleaks |
| 3 | Docker Build & Scan | Buildx + Trivy (HIGH/CRITICAL fail) |
| 4 | Deploy | Run container, smoke test, only on `main` push |

## Branching strategy (GitFlow-lite)

- `main` — production-ready; protected, requires PR.
- `develop` — integration branch.
- `feature/*` — short-lived feature branches off `develop`.

A merge from `feature/devops-enhancement` to `develop`, then `develop` to `main` simulates the full GitFlow promotion.
