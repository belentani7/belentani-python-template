# {{cookiecutter.project_name}}

{{cookiecutter.description}}

Canonical Python backend template for the Belentani ecosystem — FastAPI + Pydantic + SQLModel + uv + Ruff + pytest + OpenTelemetry.

## Quick Start

```bash
# Instalar uv (gestor de paquetes ultra-rápido)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear entorno y instalar dependencias
uv sync --all-extras

# Variables de entorno
cp .env.example .env
# Edita .env con tus valores

# Ejecutar en desarrollo
uv run uvicorn {{cookiecutter.project_slug}}.main:app --reload

# Tests
uv run pytest

# Lint + format
uv run ruff check . --fix
uv run ruff format .

# Typecheck
uv run mypy src/
```

## Stack

| Capa | Tecnología | Versión |
|------|------------|---------|
| **Framework** | FastAPI | 0.115+ |
| **Validación** | Pydantic v2 | 2.10+ |
| **ORM** | SQLModel | 0.0.22+ |
| **DB Driver** | asyncpg | 0.29+ |
| **Cache/Queue** | Redis | 5.2+ |
| **Auth** | python-jose + passlib | 3.3+ / 1.7+ |
| **Logging** | structlog + python-json-logger | 24.1+ / 2.0+ |
| **Gestor Paquetes** | uv | latest |
| **Lint/Format** | Ruff | 0.8+ |
| **Typecheck** | mypy | 1.11+ |
| **Tests** | pytest + pytest-asyncio | 8.3+ / 0.23+ |
| **Observabilidad** | OpenTelemetry + Sentry (opcional) | 1.27+ / 2.1+ |

## Arquitectura (Clean Architecture)

```
src/
├── {{project_slug}}/
│   ├── domain/              # Entidades, Value Objects, Domain Events, Repository Ports
│   │   ├── entities.py      # Entity, EntityId, RepositoryPort, DomainEvent
│   │   └── value_objects.py # (añadir según necesidad)
│   ├── application/         # Use Cases, DTOs, EventPublisher
│   │   └── use_cases.py     # UseCase, UseCaseInput/Output, EventPublisher, BaseService
│   ├── infrastructure/      # Adapters: DB, HTTP, Queue, Storage, Auth
│   │   ├── persistence/     # SQLModel repositories
│   │   ├── http/            # Cliente HTTP externo
│   │   └── queue/           # Celery/RQ workers
│   ├── interfaces/          # HTTP Routes, CLI, GraphQL
│   │   └── api/
│   │       └── v1.py        # FastAPI routers
│   ├── config/
│   │   └── settings.py      # Pydantic Settings (env-based)
│   └── main.py              # App factory + lifespan + middleware
├── tests/
│   ├── unit/                # Tests rápidos, aislados
│   ├── integration/         # Requieren DB/Redis reales
│   ├── e2e/                 # Full stack
│   └── conftest.py          # Fixtures compartidas
└── scripts/
    └── dev.py               # Helpers de desarrollo
```

## Principios

- **Núcleo independiente**: Dominio usa solo stdlib — sin FastAPI, SQLModel, etc.
- **Adaptadores intercambiables**: Memoria, PostgreSQL, SQLite, FastAPI, CLI se conectan sin tocar dominio.
- **Contratos explícitos**: Puertos definidos con `Protocol` — implementaciones sustituibles en tests/producción.
- **Fallos controlados**: API devuelve JSON consistente, no expone excepciones internas.
- **Contenido separado**: Entidades y contratos sin datos reales.

## Convenciones

- **Type hints obligatorios** — sin `Any`, returns explícitos
- **Dataclasses con `slots=True`** — rendimiento + inmutabilidad
- **Errores como valores** — `Result[T, E]` pattern, no excepciones en dominio
- **Commits convencionales** — `feat:`, `fix:`, `perf:`, `docs:`, `chore:`
- **Tests FIRST** — `pytest` antes de implementar (TDD)

## Variables de Entorno

Ver `.env.example`. **Nunca** commitees `.env`.

```bash
cp .env.example .env
# Edita con tus valores
```

## Despliegue

```bash
# Build imagen Docker
docker build -t {{cookiecutter.project_slug}} .

# Ejecutar con uvicorn (producción)
uv run uvicorn {{cookiecutter.project_slug}}.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Licencia

MIT — Úsalo libremente en proyectos institucionales.