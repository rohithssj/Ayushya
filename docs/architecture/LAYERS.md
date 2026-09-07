# AYUSHYA — Architecture Layer Specifications

## Four-Layer Architecture Overview

Each feature in AYUSHYA under `src/features/[feature-name]/` strictly enforces a clean 4-layer separation:

```text
Presentation
     ↓
Application
     ↓
Domain
     ↑
Infrastructure
```

### 1. Presentation Layer (`src/features/[feature]/presentation/`)
- UI components, page layouts, forms, display formatters.
- Manages user interaction and UI presentation state.
- **Rule**: Must not contain database logic, LLM calls, RAG logic, or business rules.

### 2. Application Layer (`src/features/[feature]/application/`)
- Use cases, application services, and workflow orchestration.
- Coordinates domain logic and delegates to infrastructure interfaces.
- **Rule**: Agnostic of framework UI or specific database implementations.

### 3. Domain Layer (`src/features/[feature]/domain/`)
- Pure business models, domain entities, value objects, and core business/regulatory rules.
- Defines domain interfaces for external infrastructure services.
- **Rule**: Has zero dependencies on outer layers or external frameworks.

### 4. Infrastructure Layer (`src/features/[feature]/infrastructure/`)
- Implementations of database access, vector search, LLM integrations, document ingestion, and external APIs.
- Implements interfaces defined in the domain/application layers.
- **Rule**: Outer dependency layer; encapsulated away from presentation and domain logic.
