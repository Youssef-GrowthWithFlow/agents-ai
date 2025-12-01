# AI Coding Agent Instructions

## Project Overview
This is a full-stack AI chat application using **FastAPI (Python)** for the backend and **React 19 (TypeScript)** for the frontend. The project uses Docker Compose for orchestration.

## Architecture & Core Components

### Backend (`/backend`)
- **Framework**: FastAPI with Uvicorn.
- **AI Integration**: Google GenAI (Gemini) via `google-genai` library.
- **Structure**:
  - `main.py`: Entry point, CORS config, router inclusion.
  - `routers/`: API route definitions (e.g., `chat.py`).
  - `services/`: Business logic and external API calls (e.g., `gemini_service.py`).
- **Port**: Runs on port `8000` inside container, exposed as `8001`.

### Frontend (`/frontend`)
- **Framework**: React 19 + Vite.
- **Language**: TypeScript.
- **Styling**: **CSS Modules** (`*.module.css`) with CSS variables defined in `src/index.css`. **Do not use Tailwind CSS** unless explicitly requested to migrate.
- **State Management**: Custom hooks (e.g., `useChatMessages`).
- **Port**: Runs on port `5173` inside container, exposed as `5174`.

### Infrastructure
- **Docker**: `docker-compose.yml` orchestrates both services with volume mounts for hot reloading.
- **Communication**: Frontend calls Backend via REST API at `http://localhost:8001/api`.

## Developer Workflows

### Running the Project
- **Start**: `docker-compose up --build` (preferred) or `docker-compose up`.
- **Backend Local**: `cd backend && uvicorn main:app --reload --port 8001`.
- **Frontend Local**: `cd frontend && npm run dev`.

### Testing
- **E2E**: Playwright tests in `frontend/tests/`.
  - Run: `cd frontend && npx playwright test`.
  - Key file: `frontend/tests/chat.spec.ts`.

## Coding Conventions

### Frontend (React/TypeScript)
- **Components**: Functional components. Use named exports.
- **Styling**: Use CSS Modules. Import as `import styles from './Component.module.css'`.
- **Theming**: Use CSS variables from `src/index.css` (e.g., `var(--color-bg)`, `var(--space-md)`).
- **Directory Structure**:
  - `components/`: UI components grouped by feature (e.g., `chat/`, `common/`).
  - `services/`: API clients (e.g., `chat.service.ts`).
  - `hooks/`: Custom React hooks.

### Backend (Python/FastAPI)
- **Type Hinting**: Use Python type hints everywhere.
- **Routers**: Keep `main.py` clean; put routes in `routers/`.
- **Services**: Encapsulate logic in `services/` classes/functions.

## Common Patterns & Gotchas
- **API URL**: The frontend currently hardcodes the API URL (`http://localhost:8001/api/chat`) in `services/chat.service.ts`. Be aware of this when debugging connection issues.
- **React 19**: This project uses React 19. Be mindful of new features or deprecations.
- **Docker Networking**: Frontend runs in browser (host network), so it calls `localhost:8001`. Backend calls external APIs (Gemini) from within the container.
