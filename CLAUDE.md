# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---
title: "AI Agent Guide - Kinder Denkspiele"
purpose: "Entry point for AI agents working on this codebase"
audience: "AI agents (Claude, GPT, Cursor)"
last_updated: "2025-11-02"
version: "3.0"
keywords: ["sveltekit", "svelte-5", "tailwind-v4", "mongodb", "fastapi", "german", "games", "kids", "llm"]
---

# 🤖 AI Agent Guide - Kinder Denkspiele

**Last Updated:** 2025-11-02
**Primary Purpose:** Kid-friendly German language cognitive training games
**Tech Stack:** SvelteKit 2.x + Svelte 5 + Tailwind CSS v4 + MongoDB + FastAPI (Python)

---

## 📍 Start Here

This is the **entry point** for AI agents working on this codebase. Read this first to understand the project structure, then navigate to specific docs as needed.

### Quick Context
- **Target Users:** Children aged 4-10 years
- **Language:** German
- **Deployment:** Local server (SvelteKit + FastAPI backend)
- **Authentication:** Two-tier system (site-wide + admin)
- **Current State:** Production with 5 games
  - Verbal Memory (German word recognition)
  - Visual Memory (grid-based spatial memory)
  - Reaction Time (speed test)
  - Logic Lab (LLM-powered adaptive puzzles)
  - Märchenweber (LLM-powered interactive storytelling - **external FastAPI service**)
- **Architecture:** Layered monorepo with external microservice
- **LLM Integration:**
  - Logic Lab: OpenRouter + Gemini 2.5 Flash (integrated in SvelteKit)
  - Märchenweber: FastAPI backend with OpenRouter + multiple LLM agents

---

## 📚 Documentation Map

### Core Documentation
1. **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System architecture, data flow, design patterns
2. **[README.md](./README.md)** - Human-readable overview, setup instructions
3. **[TECH-STACK.md](./docs/TECH-STACK.md)** - Tech stack versions, gotchas
4. **[QUICKSTART.md](./docs/QUICKSTART.md)** - Get up and running quickly
5. **[API-REFERENCE.md](./docs/API-REFERENCE.md)** - API endpoint documentation

### Customization & Troubleshooting
6. **[THEMING.md](./docs/THEMING.md)** - UI customization
7. **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** - Common issues and solutions
8. **[DECISIONS.md](./docs/DECISIONS.md)** - Technical choices and rationale
9. **[AUTH.md](./docs/AUTH.md)** - Two-tier authentication system

### Game-Specific Documentation
- **Logic Lab:** [docs/LOGIC-LAB.md](./docs/LOGIC-LAB.md) - LLM-powered adaptive puzzles
- **Märchenweber:** [backend/CLAUDE.md](./backend/CLAUDE.md) - FastAPI storytelling backend

---

## 🔍 Quick Reference for AI Queries

<!-- Optimized for conversational AI queries -->

### "How do I..."
- **Add a new game** → [ARCHITECTURE.md](./docs/ARCHITECTURE.md) extension points
- **Modify Logic Lab prompts** → [src/lib/prompts/CLAUDE.md](./src/lib/prompts/CLAUDE.md) (YAML editing)
- **Modify Märchenweber** → [backend/CLAUDE.md](./backend/CLAUDE.md) (FastAPI + Python)
- **Change theme colors** → [THEMING.md](./docs/THEMING.md)
- **Add/modify words** → Edit `src/lib/data/word-pools.ts`
- **Create a component** → [src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md)
- **Add an API endpoint** → [src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md)

### "Where is..."
- **User data** → MongoDB via `src/lib/repositories/`
- **Game logic** → `src/lib/services/` ([CLAUDE.md](./src/lib/services/CLAUDE.md))
- **LLM prompts** → `src/lib/prompts/` ([CLAUDE.md](./src/lib/prompts/CLAUDE.md))
- **API endpoints** → `src/routes/api/` ([CLAUDE.md](./src/routes/api/CLAUDE.md))
- **UI components** → `src/lib/components/` ([CLAUDE.md](./src/lib/components/CLAUDE.md))
- **Type definitions** → `src/lib/types/index.ts`
- **Game pages** → `src/routes/game/` ([CLAUDE.md](./src/routes/game/CLAUDE.md))
- **Märchenweber backend** → `backend/` ([CLAUDE.md](./backend/CLAUDE.md))

### "What is..."
- **Svelte version** → Svelte 5 with runes (see [Critical Concepts](#critical-concepts))
- **Tailwind version** → Tailwind CSS v4 (see [Critical Concepts](#critical-concepts))
- **Database** → MongoDB (shared between SvelteKit and FastAPI)
- **Architecture** → Layered with external microservice ([ARCHITECTURE.md](./docs/ARCHITECTURE.md))
- **Authentication** → Two-tier: site-wide + admin ([AUTH.md](./docs/AUTH.md))

---

## 📂 Module-Specific Documentation

Each major directory has its own CLAUDE.md with focused context:

### Core Library (`src/lib/`)
- **[src/lib/CLAUDE.md](./src/lib/CLAUDE.md)** - Overview of shared utilities and types
- **[src/lib/services/CLAUDE.md](./src/lib/services/CLAUDE.md)** - Game engines & business logic (8 services)
- **[src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md)** - Reusable UI components (9 components)
- **[src/lib/repositories/CLAUDE.md](./src/lib/repositories/CLAUDE.md)** - Database operations
- **[src/lib/prompts/CLAUDE.md](./src/lib/prompts/CLAUDE.md)** - LLM prompt templates (YAML + Jinja2)

### Routes (`src/routes/`)
- **[src/routes/CLAUDE.md](./src/routes/CLAUDE.md)** - Routing structure
- **[src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md)** - API endpoints
- **[src/routes/game/CLAUDE.md](./src/routes/game/CLAUDE.md)** - Game UI pages (5 games)

### Backend (`backend/`)
- **[backend/CLAUDE.md](./backend/CLAUDE.md)** - Märchenweber FastAPI service (Python)

---

## 🎯 Critical Concepts

### 1. Layered Architecture

```
UI Layer → API Layer → Service Layer → Repository Layer → Database Layer
```

**Never bypass layers.** Component → API → Service → Repository → MongoDB

**See:** [ARCHITECTURE.md](./docs/ARCHITECTURE.md)

---

### 2. Svelte 5 Runes

This project uses **Svelte 5** with runes, not Svelte 4 syntax:

```typescript
// ✅ Svelte 5 (what we use)
let count = $state(0);
let doubled = $derived(count * 2);
$effect(() => { console.log(count); });

// ❌ Svelte 4 (DON'T use)
let count = 0;
$: doubled = count * 2;
```

**Key differences:** `$state()`, `$derived()`, `$effect()`, `{@render children()}`, `$props()`

**See:** [TECH-STACK.md](./docs/TECH-STACK.md)

---

### 3. Tailwind CSS v4

Uses `@import "tailwindcss";` in `src/app.css`, not `@tailwind` directives.

**See:** [TECH-STACK.md](./docs/TECH-STACK.md) for setup details

---

## 🗂️ Project Structure

```
src/
├── lib/                     # Shared code
│   ├── types/              # TypeScript types
│   ├── services/           # Game engines & LLM integration (8 services)
│   ├── repositories/       # Database operations
│   ├── components/         # Reusable UI (9 components)
│   ├── prompts/            # LLM prompt templates (YAML + Jinja2)
│   ├── data/               # Static data (word pools)
│   └── db/                 # MongoDB connection
│
├── routes/                  # SvelteKit routes
│   ├── +page.svelte        # Home page (game selection)
│   ├── login/              # Site-wide authentication
│   ├── admin/              # Admin panel
│   ├── api/                # API endpoints (see API-REFERENCE.md)
│   ├── game/               # Game UI pages (5 games)
│   └── stats/[userId]/     # Historical stats
│
backend/                     # Märchenweber FastAPI service
├── app/                     # FastAPI application
│   ├── main.py             # FastAPI app
│   ├── services/           # LLM orchestration
│   └── routers/            # API routes
└── config.yaml              # LLM prompts & configuration
```

**See module-specific CLAUDE.md files** for detailed information about each directory.

---

## 🚨 Critical Gotchas

### 1. Environment Variables
**Required in `.env`:**
```bash
MONGODB_URI=mongodb://localhost:27017/humanbenchmark
GLOBA_SITE_PASSWORD=your_password_here        # Note: typo in var name
OPENROUTER_API_KEY=sk-or-v1-...               # For LLM features
MAERCHENWEBER_API_URL=http://localhost:8000   # FastAPI backend
MAERCHENWEBER_API_KEY=your_api_key            # Backend API key
```

### 2. Difficulty Levels
Project uses **3 difficulty levels**: `easy`, `hard`, `extra-hard` (not just 2)

### 3. Svelte 5 & Tailwind v4
- **Svelte 5:** Use `$state()`, `$derived()`, not `$:` reactive declarations
- **Tailwind v4:** Use `@import "tailwindcss";` not `@tailwind` directives

### 4. Two Services
- **SvelteKit** (port 5173): Main app + 4 games
- **FastAPI** (port 8000): Märchenweber storytelling game

**See:** [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for more issues

---

## 🚀 Quick Start

### Prerequisites
- Node.js 24+ (or 22.12+)
- Docker & Docker Compose
- Python 3.12+ (for Märchenweber backend)

### Running the App

```bash
# 1. Start MongoDB
docker-compose up -d

# 2. Start SvelteKit dev server
npm run dev

# 3. (Optional) Start Märchenweber backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# 4. Open browser
# http://localhost:5173
```

**See:** [QUICKSTART.md](./docs/QUICKSTART.md) for detailed setup instructions

---

## 🧪 Testing

```bash
npm test              # Run tests (watch mode)
npm test -- --run     # Run once
npm run check         # Type check
```

**Test files:** `src/lib/services/*.test.ts`

**See code for test details** (avoid duplicating metrics in docs)

---

## 📞 Command Reference

| Task | Command |
|------|---------|
| Start dev server | `npm run dev` |
| Type check | `npm run check` |
| Start MongoDB | `docker-compose up -d` |
| Start Märchenweber | `cd backend && uv run uvicorn app.main:app --reload` |
| Run tests | `npm test` |
| Build | `npm run build` |

**See:** [QUICKSTART.md](./docs/QUICKSTART.md) for full command list

---

## 📖 Related Documentation

**Start with:**
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System design
- [QUICKSTART.md](./docs/QUICKSTART.md) - Setup guide
- [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) - Common issues

**Game-specific:**
- [LOGIC-LAB.md](./docs/LOGIC-LAB.md) - LLM puzzle game
- [backend/CLAUDE.md](./backend/CLAUDE.md) - Märchenweber storytelling

**Customization:**
- [THEMING.md](./docs/THEMING.md) - UI styling
- [AUTH.md](./docs/AUTH.md) - Authentication
- [API-REFERENCE.md](./docs/API-REFERENCE.md) - API endpoints
