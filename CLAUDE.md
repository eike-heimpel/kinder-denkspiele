# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---
title: "AI Agent Guide - Kinder Denkspiele"
purpose: "Entry point for AI agents working on this codebase"
audience: "AI agents (Claude, GPT, Cursor)"
last_updated: "2025-11-01"
version: "2.1"
keywords: ["sveltekit", "svelte-5", "tailwind-v4", "mongodb", "german", "games", "kids", "layered-architecture"]
---

# 🤖 AI Agent Guide - Kinder Denkspiele

**Last Updated:** 2025-11-01
**Primary Purpose:** Kid-friendly German language cognitive training games
**Tech Stack:** SvelteKit 2.x + Svelte 5 + Tailwind CSS v4 + MongoDB + Docker

---

## 📍 Start Here

This is the **entry point** for AI agents working on this codebase. Read this first to understand the project structure, then navigate to specific docs as needed.

### Quick Context
- **Target Users:** Children aged 5-8 years
- **Language:** German
- **Deployment:** Local server only (no authentication needed)
- **Current State:** MVP with two games (Verbal Memory, Visual Memory)
- **Architecture:** Layered, decoupled, extensible

---

## 📚 Documentation Map

### For Understanding the System
1. **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Deep dive into layered architecture, data flow, design patterns
2. **[README.md](./README.md)** - Human-readable overview, setup instructions, features
3. **[TECH-STACK.md](./docs/TECH-STACK.md)** - Detailed tech stack info, version specifics, gotchas

### For Making Changes
4. **[THEMING.md](./docs/THEMING.md)** - Customizing colors, animations, UI components
5. **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** - Common issues and solutions
6. **[DECISIONS.md](./docs/DECISIONS.md)** - Why we made specific technical choices
7. **[AUTH.md](./docs/AUTH.md)** - Password authentication implementation

### For Development
8. **[QUICKSTART.md](./docs/QUICKSTART.md)** - Get up and running quickly
9. **[API-REFERENCE.md](./docs/API-REFERENCE.md)** - Complete API endpoint documentation

---

## 🔍 Quick Reference for AI Queries

<!-- Optimized for conversational AI queries -->

### "How do I..."
- **Add a new game** → [Common Tasks > Adding a New Game](#adding-a-new-game)
- **Change theme colors** → [Changing Theme Colors](#changing-theme-colors)
- **Fix Tailwind issues** → [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md#tailwind-not-working)
- **Add/modify words** → [Modifying Word Pools](#modifying-word-pools)
- **Test the API** → [API-REFERENCE.md](./docs/API-REFERENCE.md#testing)
- **Create a new component** → [src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md)
- **Add an API endpoint** → [src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md)

### "Where is..."
- **User data stored** → MongoDB via `UserRepository` ([ARCHITECTURE.md](./docs/ARCHITECTURE.md#database-schema))
- **Game logic** → `src/lib/services/` ([src/lib/services/CLAUDE.md](./src/lib/services/CLAUDE.md))
- **API endpoints** → `src/routes/api/` ([src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md))
- **UI components** → `src/lib/components/` ([src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md))
- **Type definitions** → `src/lib/types/index.ts` ([src/lib/CLAUDE.md](./src/lib/CLAUDE.md))
- **Database operations** → `src/lib/repositories/` ([src/lib/repositories/CLAUDE.md](./src/lib/repositories/CLAUDE.md))
- **Game pages** → `src/routes/game/` ([src/routes/game/CLAUDE.md](./src/routes/game/CLAUDE.md))

### "What is..."
- **The Svelte version** → Svelte 5 with runes ([Svelte 5 Runes](#svelte-5-runes))
- **The Tailwind version** → Tailwind CSS v4 ([Tailwind CSS v4](#tailwind-css-v4))
- **The database** → MongoDB with repositories ([ARCHITECTURE.md](./docs/ARCHITECTURE.md#database-schema))
- **The architecture** → Layered, decoupled ([Layered Architecture](#layered-architecture))
- **The testing approach** → Vitest unit tests + manual Playwright ([Testing](#testing))

---

## 📂 Module-Specific Documentation

For detailed information about specific parts of the codebase, see these module-level guides:

### Core Library (`src/lib/`)
- **[src/lib/CLAUDE.md](./src/lib/CLAUDE.md)** - Shared utilities, types, and data layer overview
- **[src/lib/services/CLAUDE.md](./src/lib/services/CLAUDE.md)** - Game engines & business logic
- **[src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md)** - Reusable UI components
- **[src/lib/repositories/CLAUDE.md](./src/lib/repositories/CLAUDE.md)** - Database operations & data access

### Routes (`src/routes/`)
- **[src/routes/CLAUDE.md](./src/routes/CLAUDE.md)** - Routing structure overview
- **[src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md)** - API endpoint implementation
- **[src/routes/game/CLAUDE.md](./src/routes/game/CLAUDE.md)** - Game page components & UI logic

**💡 Tip:** When working on a specific module, read the module-level CLAUDE.md for focused context.

---

## 🎯 Core Concepts

### 1. Layered Architecture (CRITICAL)

```
UI Layer (Svelte 5 Components)
    ↓
API Layer (SvelteKit Server Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database Layer (MongoDB)
```

**IMPORTANT:** Never bypass layers. Always go through the proper abstraction.

**Example:** 
- ❌ DON'T: Access MongoDB directly from a component
- ✅ DO: Component → API → Service → Repository → Database

**See:** [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for complete details

---

### 2. Svelte 5 Runes (CRITICAL)

This project uses **Svelte 5**, which has a completely different syntax from Svelte 4:

```typescript
// ✅ Svelte 5 (what we use)
let count = $state(0);
let doubled = $derived(count * 2);
$effect(() => { console.log(count); });

// ❌ Svelte 4 (DON'T use this)
let count = 0;
$: doubled = count * 2;
$: console.log(count);
```

**Key Differences:**
- Use `$state()` instead of plain `let` for reactive variables
- Use `$derived()` instead of `$:` for computed values
- Use `$effect()` instead of `$:` for side effects
- Use `{@render children()}` instead of `<slot />`
- Props: `let { propName } = $props()` instead of `export let propName`

**See:** Search "Svelte 5 runes" in codebase for examples

---

### 3. Tailwind CSS v4 (CRITICAL)

This project uses **Tailwind CSS v4**, which has different syntax from v3:

```css
/* ✅ Tailwind v4 (what we use) */
@import "tailwindcss";

/* ❌ Tailwind v3 (DON'T use this) */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Configuration:**
- Import in `src/app.css` with `@import "tailwindcss";`
- Vite plugin configured in `vite.config.ts`
- No `tailwind.config.js` needed for basic usage

**See:** [TECH-STACK.md](./docs/TECH-STACK.md#tailwind-v4) for details

---

## 🗂️ Project Structure

```
src/
├── lib/
│   ├── types/              # All TypeScript type definitions (index.ts is central)
│   ├── db/                 # MongoDB connection (singleton client)
│   ├── repositories/       # Data access layer (User, GameSession)
│   ├── services/           # Business logic (GameEngine, WordService, etc.)
│   ├── data/               # Static data (word-pools.ts has 145 German words)
│   ├── components/         # Reusable UI (Button, Card, GameStats)
│   └── auth/               # Password authentication (gitignored password.ts)
│
└── routes/                 # SvelteKit routes
    ├── +layout.svelte      # Global layout (imports CSS)
    ├── +page.svelte        # Home page
    ├── login/              # Login page for auth
    ├── api/                # API endpoints (/users, /game/*/start, /game/*/answer, etc.)
    ├── game/               # Game pages (verbal-memory, visual-memory, reaction-time)
    └── stats/[userId]/     # Historical stats page
```

**Each major directory has its own CLAUDE.md** - see [Module-Specific Documentation](#-module-specific-documentation) below.

---

## 🔑 Key Files

### Configuration Files
- `package.json` - Dependencies (MongoDB, Svelte 5, Tailwind v4)
- `vite.config.ts` - Vite config with Tailwind plugin
- `svelte.config.js` - SvelteKit config
- `docker-compose.yml` - MongoDB container

### Entry Points
- `src/app.html` - HTML template
- `src/app.css` - Global CSS with Tailwind import
- `src/routes/+layout.svelte` - Root layout
- `src/routes/+page.svelte` - Home page

### Core Logic
- `src/lib/services/game-engine.service.ts` - Main game logic
- `src/lib/services/word.service.ts` - Word selection
- `src/lib/repositories/*.ts` - Database operations

---

## 🚨 Critical Gotchas

### 1. Tailwind v4 Import Location
**Problem:** Tailwind classes not applying  
**Cause:** Wrong import syntax or location  
**Solution:** Must use `@import "tailwindcss";` in `src/app.css`  
**See:** [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md#tailwind-not-working)

### 2. Environment Variables
**Required:** `.env` file in project root with:
```bash
MONGODB_URI=mongodb://localhost:27017/humanbenchmark
```
**Type declaration:** `src/env.d.ts` declares the type for `MONGODB_URI`
**Error:** If you see "MONGODB_URI is not set", check that `.env` exists and has this variable

### 3. Svelte 5 Slot Syntax
**Problem:** `<slot />` not working  
**Cause:** Svelte 5 uses different syntax  
**Solution:** Use `{@render children()}` with `let { children } = $props()`

### 4. Node Version
**Problem:** Installation fails  
**Cause:** Need Node 24+ or Node 22.12+  
**Solution:** Use `nvm install 24 && nvm use 24`

**See:** [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for more issues

---

## 🔄 Common Tasks

### Adding a New Game

1. **Define types** in `src/lib/types/index.ts`:
```typescript
export type GameType = 'verbal-memory' | 'new-game';
```

2. **Create service** in `src/lib/services/`:
```typescript
// new-game.service.ts
export class NewGameEngine { ... }
```

3. **Add API routes** in `src/routes/api/game/new-game/`:
- `start/+server.ts`
- `action/+server.ts`
- `stats/+server.ts`

4. **Create UI page** in `src/routes/game/new-game/+page.svelte`

5. **Update home page** to show new game option

**See:** [ARCHITECTURE.md](./docs/ARCHITECTURE.md#extension-points) for details

---

### Modifying Word Pools

**File:** `src/lib/data/word-pools.ts`

```typescript
export const germanWordPools: WordPool = {
    easy: ['Hund', 'Katze', ...],  // 70 words for ages 5-6
    hard: ['Schmetterling', ...],   // 75 words for ages 7-8
};
```

**Guidelines:**
- Keep easy words to 1-2 syllables
- Hard words can be compound words (3+ syllables)
- All words must be German nouns
- Avoid violent, scary, or inappropriate words

---

### Changing Theme Colors

**File:** `src/lib/theme.ts` (reference only, not used in CSS)  
**Actual styling:** Inline Tailwind classes in components

**Example:** Change home page gradient:
```svelte
<!-- File: src/routes/+page.svelte -->
<div class="bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400">
    <!-- Change colors here -->
</div>
```

**See:** [THEMING.md](./docs/THEMING.md) for complete guide

---

## 📊 Data Flow (High-Level)

**Starting a game:**
```
UI (+page.svelte) → API (/api/game/*/start) → GameEngine.startGame()
→ GameSessionRepository.create() → MongoDB → WordService.getRandomWord()
→ Return { sessionId, currentWord, score, lives } → UI renders
```

**Submitting an answer:**
```
UI (submitAnswer) → API (/api/game/*/answer) → GameEngine.loadGame()
→ GameSessionRepository.findById() → GameEngine.submitAnswer()
→ GameSessionRepository.update() → GameEngine.nextWord() or endGame()
→ Return updated state → UI updates
```

**See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed data flow diagrams.**

---

## 🧪 Testing

### Automated Tests (Vitest)

**Run tests:**
```bash
npm test                              # Run all tests (watch mode)
npm test -- --run                     # Run once (no watch)
npm test word.service.test.ts         # Run specific test file
npm test -- --watch                   # Explicit watch mode
npm run test:ui                       # Visual test UI (browser)
```

**Test files:**
- `src/lib/services/game-engine.test.ts` - Verbal Memory GameEngine (12 tests)
- `src/lib/services/word.service.test.ts` - Word selection logic (20 tests)
- `src/lib/services/reaction-time.test.ts` - Reaction Time engine (19 tests)
- **Total:** 51 tests (50 passing, 1 skipped)

**Coverage:**
- **GameEngine:** Game logic, score, lives, word selection, edge cases, game over, no consecutive duplicates
- **WordService:** Word pool initialization, random word selection, exclusion logic, seen word selection, randomness validation, difficulty-specific behavior
- **ReactionTimeEngine:** Round logic, timing validation, game state management

---

## 🛠️ Development Workflow

### Starting Development

```bash
# 1. Start MongoDB
docker-compose up -d

# 2. Start dev server
npm run dev

# 3. Open browser
# http://localhost:5173
```

### Making Changes

```bash
# 1. Make your changes
# 2. Save files (Vite hot-reloads automatically)
# 3. Test in browser
# 4. Check for errors
npm run check
```

### Before Committing

```bash
# 1. Run tests
npm test -- --run

# 2. Type check
npm run check

# 3. Test manually in browser

# 4. Write descriptive commit
git add -A
git commit -m "Clear description of what and why"
```

---

## 📝 Coding Standards

### TypeScript
- Always define interfaces for complex objects
- Use type narrowing with type guards
- Avoid `any` - use `unknown` if truly unknown
- Export types from `src/lib/types/index.ts`

### Svelte Components
- Use Svelte 5 runes (`$state`, `$derived`, `$effect`)
- Props via `$props()` destructuring
- Children via `{@render children()}`
- Keep components focused and reusable

### CSS
- Use Tailwind utility classes
- Avoid custom CSS when possible
- Component-specific styles in `<style>` tags
- Use Tailwind v4 syntax

### API Design
- RESTful endpoints
- JSON request/response
- Proper HTTP status codes
- Error handling with try/catch
- Validate inputs

---

## 🎯 Project Goals

### Current State (MVP)
- ✅ Three games:
  - **Verbal Memory** (145 German words)
  - **Visual Memory** (3x3 or 4x4 grid, science-backed working memory training)
  - **Reaction Time** (5 rounds, measures processing speed)
- ✅ User management
- ✅ Two difficulty levels (ages 5-6 and 7-8)
- ✅ Score tracking per game
- ✅ Historical stats page (supports all games)
- ✅ Tablet-optimized UI
- ✅ Round counter
- ✅ MongoDB persistence
- ✅ Unit tests (51 total tests, 50 passing, 1 skipped)
  - GameEngine: 12 tests
  - WordService: 20 tests
  - ReactionTimeEngine: 19 tests
- ✅ Manual testing with Playwright for Visual Memory and Reaction Time

### Future Expansion
- [ ] More games (number memory, sequence memory, etc.)
- [ ] Leaderboards
- [ ] User profiles with avatars
- [ ] Achievements/badges
- [ ] Sound effects
- [ ] Multi-language support
- [ ] Remote MongoDB deployment

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start dev server | `npm run dev` |
| Type check | `npm run check` |
| Type check (watch) | `npm run check:watch` |
| Start MongoDB | `docker-compose up -d` |
| Stop MongoDB | `docker-compose down` |
| View MongoDB data | `docker exec -it humanbenchmark-mongo mongosh humanbenchmark` |
| Install deps | `npm install` |
| Build for production | `npm run build` |
| Preview build | `npm run preview` |
| Run tests | `npm test` |
| Run tests (once) | `npm test -- --run` |
| Test UI | `npm run test:ui` |

---

## 🔐 Authentication

This project uses simple password authentication for site-wide access control.

**Password location:** `src/lib/auth/password.ts` (gitignored)
**Implementation:** See [AUTH.md](./docs/AUTH.md) for complete details
**Endpoints:** Login page at `/login`, auth check in `src/hooks.server.ts`

---

**Next Steps:**
(only read if needed for your task!)

1. Read [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for system design
2. Read [TECH-STACK.md](./docs/TECH-STACK.md) for tech details
3. Run through [QUICKSTART.md](./docs/QUICKSTART.md) to test everything
4. Check [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) if issues arise
