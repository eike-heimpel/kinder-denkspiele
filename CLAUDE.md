---
title: "AI Agent Guide - Kinder Denkspiele"
purpose: "Entry point for AI agents working on this codebase"
audience: "AI agents (Claude, GPT, Cursor)"
last_updated: "2025-10-03"
version: "2.0"
keywords: ["sveltekit", "svelte-5", "tailwind-v4", "mongodb", "german", "games", "kids", "layered-architecture"]
---

# 🤖 AI Agent Guide - Kinder Denkspiele

**Last Updated:** 2025-10-03 (ONLY UPDATE AFTER LOOKING UP TODAYS DATE, DONT RECALL IT FROM MEMORY)  
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
1. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Deep dive into layered architecture, data flow, design patterns
2. **[README.md](./README.md)** - Human-readable overview, setup instructions, features
3. **[TECH-STACK.md](./TECH-STACK.md)** - Detailed tech stack info, version specifics, gotchas

### For Making Changes
4. **[THEMING.md](./THEMING.md)** - Customizing colors, animations, UI components
5. **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
6. **[DECISIONS.md](./DECISIONS.md)** - Why we made specific technical choices

### For Development
7. **[QUICKSTART.md](./QUICKSTART.md)** - Get up and running quickly
8. **[API-REFERENCE.md](./API-REFERENCE.md)** - Complete API endpoint documentation

---

## 🔍 Quick Reference for AI Queries

<!-- Optimized for conversational AI queries -->

### "How do I..."
- **Add a new game** → [Common Tasks > Adding a New Game](#adding-a-new-game)
- **Change theme colors** → [Changing Theme Colors](#changing-theme-colors)
- **Fix Tailwind issues** → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#tailwind-not-working)
- **Add/modify words** → [Modifying Word Pools](#modifying-word-pools)
- **Test the API** → [API-REFERENCE.md](./API-REFERENCE.md#testing)
- **Create a new component** → [src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md)
- **Add an API endpoint** → [src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md)

### "Where is..."
- **User data stored** → MongoDB via `UserRepository` ([ARCHITECTURE.md](./ARCHITECTURE.md#database-schema))
- **Game logic** → `src/lib/services/` ([src/lib/services/CLAUDE.md](./src/lib/services/CLAUDE.md))
- **API endpoints** → `src/routes/api/` ([src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md))
- **UI components** → `src/lib/components/` ([src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md))
- **Type definitions** → `src/lib/types/index.ts` ([src/lib/CLAUDE.md](./src/lib/CLAUDE.md))
- **Database operations** → `src/lib/repositories/` ([src/lib/repositories/CLAUDE.md](./src/lib/repositories/CLAUDE.md))
- **Game pages** → `src/routes/game/` ([src/routes/game/CLAUDE.md](./src/routes/game/CLAUDE.md))

### "What is..."
- **The Svelte version** → Svelte 5 with runes ([Svelte 5 Runes](#svelte-5-runes))
- **The Tailwind version** → Tailwind CSS v4 ([Tailwind CSS v4](#tailwind-css-v4))
- **The database** → MongoDB with repositories ([ARCHITECTURE.md](./ARCHITECTURE.md#database-schema))
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

**See:** [ARCHITECTURE.md](./ARCHITECTURE.md) for complete details

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

**See:** [TECH-STACK.md](./TECH-STACK.md#tailwind-v4) for details

---

## 🗂️ Project Structure

```
src/
├── lib/
│   ├── types/              # All TypeScript type definitions
│   │   └── index.ts        # Central type exports
│   │
│   ├── db/                 # Database connection management
│   │   └── client.ts       # MongoDB singleton client
│   │
│   ├── repositories/       # Data access layer (CRUD operations)
│   │   ├── user.repository.ts
│   │   └── game-session.repository.ts
│   │
│   ├── services/           # Business logic layer
│   │   ├── word.service.ts        # Word selection logic
│   │   └── game-engine.service.ts # Game state management
│   │
│   ├── data/               # Static data
│   │   └── word-pools.ts   # German word lists (145 words)
│   │
│   └── components/         # Reusable UI components
│       ├── Button.svelte
│       ├── Card.svelte
│       └── GameStats.svelte
│
└── routes/                 # SvelteKit routes
    ├── +layout.svelte      # Global layout (imports CSS)
    ├── +page.svelte        # Home page (user selection)
    │
    ├── api/                # API endpoints
    │   ├── users/
    │   │   ├── +server.ts
    │   │   └── [id]/+server.ts
    │   └── game/
    │       └── verbal-memory/
    │           ├── start/+server.ts
    │           ├── answer/+server.ts
    │           └── stats/+server.ts
    │
    ├── game/               # Game pages
    │   └── verbal-memory/
    │       └── +page.svelte
    │
    └── stats/              # Stats pages
        └── [userId]/+page.svelte
```

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
**See:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#tailwind-not-working)

### 2. MongoDB Environment Variable
**Problem:** "MONGODB_URI is not set" error  
**Cause:** Missing environment variable type declaration  
**Solution:** Type declared in `src/env.d.ts`  
**File:** Create `.env` with `MONGODB_URI=mongodb://localhost:27017/humanbenchmark`

### 3. Svelte 5 Slot Syntax
**Problem:** `<slot />` not working  
**Cause:** Svelte 5 uses different syntax  
**Solution:** Use `{@render children()}` with `let { children } = $props()`

### 4. Node Version
**Problem:** Installation fails  
**Cause:** Need Node 24+ or Node 22.12+  
**Solution:** Use `nvm install 24 && nvm use 24`

**See:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more issues

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

**See:** [ARCHITECTURE.md](./ARCHITECTURE.md#extension-points) for details

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

**See:** [THEMING.md](./THEMING.md) for complete guide

---

## 🔍 Finding Things

### Search Patterns

**Find all API endpoints:**
```bash
find src/routes/api -name "+server.ts"
```

**Find all game pages:**
```bash
find src/routes/game -name "+page.svelte"
```

**Find all components:**
```bash
ls src/lib/components/*.svelte
```

**Find where a function is used:**
```bash
grep -r "functionName" src/
```

**Find all Svelte 5 state:**
```bash
grep -r "\$state" src/
```

---

## 📊 Data Flow Examples

### Starting a New Game

```
1. User clicks "Start Game" button
   └─ File: src/routes/+page.svelte
   
2. Navigate to game page with URL params
   └─ File: src/routes/game/verbal-memory/+page.svelte
   └─ Function: startGame()
   
3. onMount() calls API to start game
   └─ Endpoint: POST /api/game/verbal-memory/start
   └─ File: src/routes/api/game/verbal-memory/start/+server.ts
   
4. API creates GameEngine instance
   └─ File: src/lib/services/game-engine.service.ts
   └─ Function: GameEngine.startGame()
   
5. GameEngine creates game session
   └─ Calls: GameSessionRepository.create()
   └─ File: src/lib/repositories/game-session.repository.ts
   
6. Repository saves to MongoDB
   └─ Collection: game_sessions
   └─ Returns: sessionId
   
7. GameEngine gets first word
   └─ Calls: WordService.getRandomWord()
   └─ File: src/lib/services/word.service.ts
   
8. API returns game state to UI
   └─ Response: { sessionId, currentWord, score, lives }
   
9. UI renders word and buttons
   └─ Component: Card with word display and action buttons
```

---

### Submitting an Answer

```
1. User clicks "NEU" or "GESEHEN" button
   └─ File: src/routes/game/verbal-memory/+page.svelte
   └─ Function: submitAnswer('new' | 'seen')
   
2. POST request to answer endpoint
   └─ Endpoint: POST /api/game/verbal-memory/answer
   └─ Body: { sessionId, answer }
   
3. API loads game session
   └─ Calls: GameEngine.loadGame(sessionId)
   └─ Fetches: GameSessionRepository.findById()
   
4. GameEngine validates answer
   └─ Compares: user answer vs. actual state
   └─ Updates: score or lives
   
5. Repository updates MongoDB
   └─ Calls: GameSessionRepository.update()
   └─ Updates: score, lives, wordsShown
   
6. Check if game over
   └─ If lives <= 0: GameEngine.endGame()
   └─ Else: GameEngine.nextWord()
   
7. Return updated state
   └─ Response: { currentWord, score, lives, gameOver }
   
8. UI updates display
   └─ New word appears with animation
   └─ Stats component shows updated values
```

---

## 🧪 Testing

### Automated Tests

**Run tests:**
```bash
npm test              # Run tests once
npm test -- --watch   # Watch mode
npm run test:ui       # Visual UI
```

**Test files:**
- `src/lib/services/game-engine.test.ts` - GameEngine unit tests (12 tests)
- `src/lib/services/word.service.test.ts` - WordService unit tests (20 tests)

**Coverage:**
- **GameEngine:** Game logic, score, lives, word selection, edge cases, game over, no consecutive duplicates
- **WordService:** Word pool initialization, random word selection, exclusion logic, seen word selection, randomness validation, difficulty-specific behavior

### Manual Testing Checklist

**User Flow:**
- [ ] Can create new user
- [ ] Can select existing user
- [ ] Can start easy game
- [ ] Can start hard game
- [ ] Can answer correctly
- [ ] Can answer incorrectly
- [ ] Lives decrease on wrong answer
- [ ] Score increases on correct answer
- [ ] Game ends when lives reach 0
- [ ] Can replay after game over
- [ ] Can return to home page

**UI Testing:**
- [ ] Gradients visible on all pages
- [ ] Animations smooth
- [ ] Buttons responsive to hover/click
- [ ] Text readable
- [ ] Emojis display correctly
- [ ] Mobile responsive (if applicable)

**API Testing:**
```bash
# Create user
curl -X POST http://localhost:5173/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"TestUser"}'

# Get all users
curl http://localhost:5173/api/users

# Start game
curl -X POST http://localhost:5173/api/game/verbal-memory/start \
  -H "Content-Type: application/json" \
  -d '{"userId":"USER_ID","difficulty":"easy"}'
```

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

## 🔗 External Resources

### Documentation
- [Svelte 5 Docs](https://svelte.dev/docs/svelte/overview)
- [SvelteKit Docs](https://svelte.dev/docs/kit/introduction)
- [Tailwind CSS v4 Docs](https://tailwindcss.com/docs)
- [MongoDB Node.js Driver](https://www.mongodb.com/docs/drivers/node/)

### When You Need Help
1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) first
2. Search this codebase for similar examples
3. Check external docs for tech-specific issues
4. Look at git history for context: `git log --all --full-history -- path/to/file`

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
| Start MongoDB | `docker-compose up -d` |
| Stop MongoDB | `docker-compose down` |
| View MongoDB data | `docker exec -it humanbenchmark-mongo mongosh humanbenchmark` |
| Install deps | `npm install` |
| Build for production | `npm run build` |

---

## ⚡ Performance Notes

- MongoDB uses connection pooling (singleton pattern)
- Svelte 5 has fine-grained reactivity (minimal re-renders)
- Tailwind CSS is JIT compiled (only used classes)
- No client-side routing overhead (SvelteKit handles it)

---

**Next Steps:**
(only read if needed for your task!)

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
2. Read [TECH-STACK.md](./TECH-STACK.md) for tech details
3. Run through [QUICKSTART.md](./QUICKSTART.md) to test everything
4. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) if issues arise

**Happy Coding! 🤖**
