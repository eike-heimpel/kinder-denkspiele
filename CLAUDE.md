# CLAUDE.md

AI agent entry point for this codebase.

---

## 📍 Quick Context

**Target:** German cognitive games for kids (ages 4-10)
**Stack:** SvelteKit 2 + Svelte 5 + Tailwind v4 + MongoDB + FastAPI
**Games:** 5 total (3 cognitive + 2 LLM-powered)
**Architecture:** Strict layered design with FastAPI microservice

### Critical
- **Svelte 5 runes** - Use `$state()`, `$derived()`, `$effect()` (not `$:`)
- **Tailwind v4** - Use `@import "tailwindcss";` (not `@tailwind` directives)
- **3 difficulty levels** - `easy`, `hard`, `extra-hard`
- **Layer separation** - Never bypass: UI → API → Service → Repository → DB

## 📚 Documentation Index

**Core Guides:**
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System design, data flow, extension points
- [TECH-STACK.md](./docs/TECH-STACK.md) - Versions, Svelte 5 runes, Tailwind v4 setup
- [API-REFERENCE.md](./docs/API-REFERENCE.md) - All API endpoints
- [QUICKSTART.md](./docs/QUICKSTART.md) - Setup & run

**Specialized:**
- [LOGIC-LAB.md](./docs/LOGIC-LAB.md) - LLM puzzle implementation
- [backend/CLAUDE.md](./backend/CLAUDE.md) - Märchenweber FastAPI service
- [AUTH.md](./docs/AUTH.md) - Two-tier auth system
- [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) - Common issues

## 🎯 Common Tasks

| Task | Location |
|------|----------|
| Add new game | [ARCHITECTURE.md](./docs/ARCHITECTURE.md) extension points |
| Modify LLM prompts | `src/lib/prompts/*.yaml` |
| Change theme | [THEMING.md](./docs/THEMING.md) |
| Add API endpoint | `src/routes/api/` |
| Create component | `src/lib/components/` |
| Modify word pools | `src/lib/data/word-pools.ts` |
| Debug issues | [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) |

**Note:** Each directory (`src/lib/services/`, `src/routes/api/`, etc.) has its own `CLAUDE.md` that will be auto-loaded when you work in that directory.

## 🚨 Gotchas

**Environment:** `.env` required with:
```bash
MONGODB_URI=mongodb://localhost:27017/humanbenchmark
GLOBA_SITE_PASSWORD=...        # Note: typo in var name
OPENROUTER_API_KEY=sk-or-v1-...
MAERCHENWEBER_API_URL=http://localhost:8000
MAERCHENWEBER_API_KEY=...
```

**Two services:**
- SvelteKit (port 5173) - Main app + 4 games
- FastAPI (port 8000) - Märchenweber only

**Setup:**
```bash
docker-compose up -d           # MongoDB
npm run dev                    # SvelteKit
cd backend && uv run uvicorn app.main:app --reload  # FastAPI (optional)
```

See [QUICKSTART.md](./docs/QUICKSTART.md) for full setup.
