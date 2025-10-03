---
title: "Lib Layer Documentation"
purpose: "Shared utilities, types, services, and data access"
parent: "../../CLAUDE.md"
last_updated: "2025-10-03"
keywords: ["lib", "shared", "types", "services", "repositories", "components", "database"]
---

# 📚 Lib Layer - Shared Code

**Layer:** Core Library  
**Location:** `src/lib/`  
**Parent Guide:** [Main CLAUDE.md](../../CLAUDE.md)

---

## 🎯 Purpose

The `lib/` directory contains all shared, reusable code that forms the foundation of the application:
- Type definitions
- Business logic (services)
- Data access (repositories)
- UI components
- Database connection
- Static data

---

## 📂 Directory Structure

```
src/lib/
├── types/              # TypeScript type definitions
│   └── index.ts        # Central type exports
│
├── services/           # Business logic & game engines
│   ├── game-engine.service.ts
│   ├── word.service.ts
│   ├── visual-memory.service.ts
│   └── reaction-time.service.ts
│
├── repositories/       # Data access layer
│   ├── user.repository.ts
│   └── game-session.repository.ts
│
├── components/         # Reusable UI components
│   ├── Button.svelte
│   ├── Card.svelte
│   ├── GameStats.svelte
│   └── VisualMemoryGrid.svelte
│
├── db/                 # Database connection
│   └── client.ts       # MongoDB singleton
│
├── data/               # Static data
│   └── word-pools.ts   # German word lists
│
└── theme.ts            # Theme configuration (reference)
```

---

## 🔗 Module-Specific Guides

For detailed information about each subdirectory:

- **[services/CLAUDE.md](./services/CLAUDE.md)** - Game engines & business logic
- **[repositories/CLAUDE.md](./repositories/CLAUDE.md)** - Database operations
- **[components/CLAUDE.md](./components/CLAUDE.md)** - Reusable UI components

---

## 🎨 Types (`types/`)

**File:** `types/index.ts`

Central location for all TypeScript type definitions.

### Key Types

```typescript
// Users
export type User = {
  _id: string;
  name: string;
  createdAt: Date;
};

// Games
export type GameType = 'verbal-memory' | 'visual-memory' | 'reaction-time';
export type DifficultyLevel = 'easy' | 'hard';

// Game Sessions
export type GameSession = {
  _id: string;
  userId: string;
  gameType: GameType;
  difficulty: DifficultyLevel;
  score: number;
  // ... game-specific fields
};
```

### Adding New Types

1. Define type in `types/index.ts`
2. Export it: `export type NewType = { ... }`
3. Import where needed: `import type { NewType } from '$lib/types'`

**See:** [Main CLAUDE.md > TypeScript Standards](../../CLAUDE.md#typescript)

---

## 🎮 Services (`services/`)

**Business logic and game engines.**

**Files:**
- `game-engine.service.ts` - Verbal memory game
- `visual-memory.service.ts` - Visual memory game
- `reaction-time.service.ts` - Reaction time game
- `word.service.ts` - Word selection logic

**See:** [services/CLAUDE.md](./services/CLAUDE.md) for detailed documentation

---

## 💾 Repositories (`repositories/`)

**Data access layer - CRUD operations.**

**Files:**
- `user.repository.ts` - User management
- `game-session.repository.ts` - Game session persistence

**See:** [repositories/CLAUDE.md](./repositories/CLAUDE.md) for detailed documentation

---

## 🧩 Components (`components/`)

**Reusable Svelte 5 UI components.**

**Files:**
- `Button.svelte` - Styled button with variants
- `Card.svelte` - Container component
- `GameStats.svelte` - Score/lives display
- `VisualMemoryGrid.svelte` - Grid for visual memory game

**See:** [components/CLAUDE.md](./components/CLAUDE.md) for detailed documentation

---

## 🗄️ Database (`db/`)

**File:** `db/client.ts`

### MongoDB Connection

Singleton pattern for database connection:

```typescript
import { connectToDatabase } from '$lib/db/client';

// In any server-side code
const db = await connectToDatabase();
const usersCollection = db.collection('users');
```

**Important:**
- Only use in server-side code (API routes, repositories)
- Connection is pooled and reused
- Environment variable: `MONGODB_URI`

**See:** [TROUBLESHOOTING.md > MongoDB Issues](../../TROUBLESHOOTING.md#mongodb-connection-failed)

---

## 📊 Data (`data/`)

**File:** `data/word-pools.ts`

Static data for games.

### Word Pools

```typescript
export const germanWordPools: WordPool = {
  easy: ['Hund', 'Katze', ...],  // 70 words (ages 5-6)
  hard: ['Schmetterling', ...],   // 75 words (ages 7-8)
};
```

**Modifying Word Pools:**
1. Edit `word-pools.ts`
2. Follow guidelines:
   - Easy: 1-2 syllables
   - Hard: 3+ syllables, compound words
   - All German nouns
   - Kid-appropriate

**See:** [Main CLAUDE.md > Modifying Word Pools](../../CLAUDE.md#modifying-word-pools)

---

## 🎨 Theme (`theme.ts`)

**File:** `theme.ts`

Reference file for theme configuration. Not actively used in CSS.

**Note:** Actual styling uses inline Tailwind classes in components.

**See:** [THEMING.md](../../THEMING.md) for customization guide

---

## 🔄 Common Patterns

### Importing from Lib

```typescript
// Types
import type { User, GameSession } from '$lib/types';

// Services
import { GameEngine } from '$lib/services/game-engine.service';
import { WordService } from '$lib/services/word.service';

// Repositories
import { UserRepository } from '$lib/repositories/user.repository';

// Components (in .svelte files)
import Button from '$lib/components/Button.svelte';
import Card from '$lib/components/Card.svelte';

// Data
import { germanWordPools } from '$lib/data/word-pools';
```

### Layer Communication

**Correct Flow:**
```
UI Component 
  → API Route 
    → Service 
      → Repository 
        → Database
```

**Never skip layers!**

---

## 🧪 Testing

### Unit Tests

Located alongside source files:
- `game-engine.test.ts` (12 tests)
- `word.service.test.ts` (20 tests)
- `reaction-time.test.ts` (19 tests)

**Run tests:**
```bash
npm test              # All tests
npm test word         # Specific test
npm test -- --watch   # Watch mode
```

**See:** [Main CLAUDE.md > Testing](../../CLAUDE.md#testing)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../CLAUDE.md) - Entry point
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System design
- [TECH-STACK.md](../../TECH-STACK.md) - Technology details
- [services/CLAUDE.md](./services/CLAUDE.md) - Business logic
- [repositories/CLAUDE.md](./repositories/CLAUDE.md) - Data access
- [components/CLAUDE.md](./components/CLAUDE.md) - UI components

---

**For working with specific modules, see their dedicated CLAUDE.md files above.**

