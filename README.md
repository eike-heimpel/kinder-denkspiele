# Kinder Denkspiele

A full-stack cognitive training game platform for German-speaking children (ages 4-10), featuring AI-powered adaptive puzzles and storytelling.

**Tech Stack:** SvelteKit 2 + Svelte 5 + TypeScript + Tailwind v4 + MongoDB + FastAPI + LLM Integration

---

## 🤖 For AI Agents

**START HERE:** [AI-GUIDE.md](./AI-GUIDE.md)

Complete documentation for AI agents includes:
- [AI-GUIDE.md](./AI-GUIDE.md) - Main entry point and navigation
- [TECH-STACK.md](./TECH-STACK.md) - Technical specifications
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [DECISIONS.md](./DECISIONS.md) - Why we made specific choices
- [API-REFERENCE.md](./API-REFERENCE.md) - Complete API documentation
- [THEMING.md](./THEMING.md) - UI customization guide

---

## 🎮 Features

### 5 Cognitive Training Games
- **Verbales Gedächtnis** 🗣️: Word recognition and working memory training
- **Visuelles Gedächtnis** 🎯: Spatial memory with adaptive grid sizes (3x3 to 4x4)
- **Reaktionszeit** ⚡: Processing speed and reaction time measurement
- **Logic Lab** 🧪: **LLM-powered adaptive logic puzzles** with real-time difficulty adjustment (Gemini 2.5 Flash)
- **Märchenweber** 📖: **AI storytelling engine** with multiple LLM agents for interactive narratives (FastAPI microservice)

### Platform Highlights
- **AI Integration**: OpenRouter + Gemini for adaptive gameplay and narrative generation
- **Microservice Architecture**: SvelteKit frontend + FastAPI backend for LLM-heavy features
- **3 Difficulty Levels**: Easy (4-6 years), Hard (7-8 years), Extra Hard (9-10 years)
- **Multi-user System**: Individual profiles with historical performance tracking
- **Two-tier Authentication**: Site-wide access control + admin panel
- **Production-ready**: Layered architecture, comprehensive error handling, unit tests

## 🏗️ Architecture

Clean layered architecture with microservice separation:

```
src/                        # SvelteKit Frontend
├── lib/
│   ├── types/             # TypeScript interfaces
│   ├── repositories/      # Database layer (MongoDB)
│   ├── services/          # Business logic (8 game engines + LLM integration)
│   ├── prompts/           # LLM prompt templates (YAML + Jinja2)
│   └── components/        # Reusable UI components
└── routes/
    ├── api/               # RESTful API endpoints
    ├── game/              # Game UI pages (5 games)
    ├── admin/             # Admin dashboard
    └── stats/             # Performance analytics

backend/                   # FastAPI Microservice
├── app/
│   ├── services/          # LLM orchestration (multi-agent)
│   └── routers/           # Story generation API
└── config.yaml            # Prompt configuration
```

**Design Principles:**
- Strict layer separation (UI → API → Service → Repository → Database)
- Dependency injection for testability
- Repository pattern for data access
- Service layer for all business logic

## 🚀 Quick Start

### Prerequisites
- Node.js 24+ (or 22.12+)
- Python 3.12+ (for Märchenweber backend)
- Docker & Docker Compose

### Installation

```bash
# 1. Install dependencies
npm install

# 2. Configure environment (.env file)
MONGODB_URI=mongodb://localhost:27017/humanbenchmark
GLOBA_SITE_PASSWORD=your_site_password
OPENROUTER_API_KEY=sk-or-v1-...
MAERCHENWEBER_API_URL=http://localhost:8000
MAERCHENWEBER_API_KEY=your_backend_key

# 3. Start MongoDB
docker-compose up -d

# 4. Start SvelteKit (port 5173)
npm run dev

# 5. Start FastAPI backend (port 8000) - optional, for Märchenweber
cd backend
uv run uvicorn app.main:app --reload
```

Open `http://localhost:5173`

## 🛠️ Key Technical Implementations

### LLM Integration
- **Logic Lab**: Adaptive puzzle generation using OpenRouter + Gemini 2.5 Flash
- **Märchenweber**: Multi-agent storytelling with configurable YAML prompts
- **Prompt Management**: Jinja2 templates with structured output validation

### Data Flow
```
User Action → SvelteKit Route → API Endpoint → Service Layer → Repository → MongoDB
                                      ↓
                              LLM Service (OpenRouter)
```

### Testing
- **32 unit tests** covering game engines and business logic
- **Type-safe** TypeScript throughout
- **Error handling** with structured logging

## 🛠️ Tech Stack

**Frontend:**
- SvelteKit 2 + Svelte 5 (with runes)
- TypeScript
- Tailwind CSS v4
- Vitest (unit tests)

**Backend:**
- FastAPI (Python microservice)
- MongoDB (shared database)
- OpenRouter (LLM gateway)
- Gemini 2.5 Flash (primary model)

**Infrastructure:**
- Docker Compose
- RESTful API design
- YAML-based configuration

## 📚 Documentation

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design and patterns
- **[API-REFERENCE.md](./docs/API-REFERENCE.md)** - Complete API documentation
- **[LOGIC-LAB.md](./docs/LOGIC-LAB.md)** - LLM puzzle implementation
- **[backend/CLAUDE.md](./backend/CLAUDE.md)** - Märchenweber storytelling engine
- **[TECH-STACK.md](./docs/TECH-STACK.md)** - Version details and gotchas

## 🔧 Development Commands

```bash
npm run dev          # Start SvelteKit dev server (port 5173)
npm run build        # Production build
npm run check        # TypeScript type checking
npm test             # Run unit tests (32 tests)
docker-compose up -d # Start MongoDB
cd backend && uv run uvicorn app.main:app --reload  # Start FastAPI (port 8000)
```

## 📄 License

Personal project for portfolio purposes.
