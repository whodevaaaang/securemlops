# Pipeline flow

```mermaid
flowchart TD
    Push[push / PR to main or develop] --> Build
    Build[Job: build<br/>flake8 · black · train model] -->|model.joblib artifact| Test
    Test[Job: test<br/>pytest --cov · bandit · gitleaks] --> Docker
    Docker[Job: docker<br/>buildx · trivy HIGH/CRITICAL] -->|image artifact| Deploy
    Deploy{ref == main?}
    Docker --> Deploy
    Deploy -- yes --> Run[Job: deploy<br/>docker run + smoke test]
    Deploy -- no --> Skip[Skip deploy]
```

## Why each gate exists

| Gate | Failure mode it catches |
|------|------------------------|
| flake8 / black | Style drift and dead code before review |
| pytest | Behavioural regressions (predict + health + auth) |
| Bandit | Python-specific insecure patterns (eval, weak crypto, hardcoded passwords) |
| Gitleaks | Hardcoded secrets accidentally committed |
| Trivy (HIGH/CRITICAL) | Vulnerable OS / Python libraries shipped in the image |
| Smoke test | Container starts but `/predict` is broken — caught before declaring deploy success |
