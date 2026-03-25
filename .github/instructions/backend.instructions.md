---
applyTo: "**/*.py"
---

Backend instructions:

- Always follow the HackSoft Django Styleguide for backend architecture and code organization:
  https://github.com/HackSoftware/Django-Styleguide

- Prefer the styleguide’s separation of concerns:
  - business logic in services
  - data fetching in selectors
  - keep views and serializers thin
  - avoid putting business logic in views, serializers, forms, model save methods, managers, querysets, or signals
  - never make external API calls directly from views; encapsulate external integrations in service layer


- When generating or editing backend code:
  - follow the existing project structure first
  - if the codebase already has local conventions, prefer those when they do not strongly conflict with the styleguide
  - keep changes minimal and consistent with surrounding files

- Follow Flake8 rules at all times.
- Write code that is Flake8-compliant.
- Avoid unused imports, unused variables, overly long lines, and inconsistent formatting.
- Prefer readable, explicit code over clever shortcuts.
