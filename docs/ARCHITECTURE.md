---
title: "Architecture Documentation"
purpose: "System design, data flow, and design patterns"
audience: "AI agents, developers"
last_updated: "2025-10-03"
keywords: ["architecture", "layered", "data-flow", "patterns", "design"]
related_docs: ["CLAUDE.md", "TECH-STACK.md", "API-REFERENCE.md"]
---

# 🏗️ Architecture Documentation

## Overview

This application follows a **layered architecture** with clear separation of concerns, making it easy to extend and maintain.

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                    UI Layer                         │
│  (Svelte 5 Components & Pages)                      │
│  - +page.svelte files                               │
│  - Reusable components                              │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│                  API Layer                          │
│  (SvelteKit Server Routes)                          │
│  - /api/users/                                      │
│  - /api/game/verbal-memory/                         │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│               Service Layer                         │
│  (Business Logic)                                   │
│  - GameEngine: Game state & rules                   │
│  - WordService: Word selection logic                │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│             Repository Layer                        │
│  (Data Access)                                      │
│  - UserRepository: CRUD for users                   │
│  - GameSessionRepository: CRUD for sessions         │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│              Database Layer                         │
│  (MongoDB Client)                                   │
│  - Connection management                            │
│  - Database instance                                │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### Starting a Game

```
User clicks "Start"
       ↓
UI Component (+page.svelte)
       ↓
API Endpoint (/api/game/verbal-memory/start)
       ↓
GameEngine.startGame(userId, difficulty)
       ↓
GameSessionRepository.create(session)
       ↓
MongoDB (game_sessions collection)
       ↓
GameEngine.nextWord() → WordService.getRandomWord()
       ↓
API returns { sessionId, currentWord, score, lives }
       ↓
UI updates with new word
```

### Submitting an Answer

```
User clicks "GESEHEN" or "NEU"
       ↓
UI Component
       ↓
API Endpoint (/api/game/verbal-memory/answer)
       ↓
GameEngine.loadGame(sessionId)
       ↓
GameSessionRepository.findById(sessionId)
       ↓
GameEngine.submitAnswer('seen' | 'new')
       ↓
GameEngine calculates if correct
       ↓
GameSessionRepository.update(sessionId, { score, lives })
       ↓
If lives > 0: nextWord()
If lives = 0: endGame()
       ↓
API returns updated game state
       ↓
UI updates
```

## Key Design Patterns

### 1. Repository Pattern
**Location**: `src/lib/repositories/`

**Purpose**: Abstracts database operations from business logic

**Benefits**:
- Easy to switch databases
- Mockable for testing
- Clear data access API

**Example**:
```typescript
class UserRepository {
  async create(name: string): Promise<User>
  async findById(id: string): Promise<User | null>
  async findAll(): Promise<User[]>
  async delete(id: string): Promise<boolean>
}
```

### 2. Service Layer Pattern
**Location**: `src/lib/services/`

**Purpose**: Contains all game logic and business rules

**Benefits**:
- Testable without UI or database
- Reusable across different games
- Clear API for game operations

**Example**:
```typescript
class GameEngine {
  async startGame(userId, difficulty): Promise<GameState>
  async submitAnswer(answer): Promise<GameState>
  async endGame(): Promise<GameState>
}
```

### 3. Strategy Pattern (Word Selection)
**Location**: `src/lib/services/word.service.ts`

**Purpose**: Encapsulates word selection logic

**Benefits**:
- Easy to change difficulty algorithms
- Can add new selection strategies
- Isolated and testable

### 4. Type-Driven Development
**Location**: `src/lib/types/`

**Purpose**: Central type definitions

**Benefits**:
- Type safety across all layers
- Self-documenting code
- Catches errors at compile time

## Component Architecture

### Reusable Components

#### Button.svelte
- **Props**: `variant`, `size`, `onclick`, `disabled`, `children`
- **Purpose**: Consistent, kid-friendly buttons
- **Variants**: primary, secondary, success, danger
- **Sizes**: sm, md, lg, xl

#### Card.svelte
- **Props**: `children`, `class`
- **Purpose**: Consistent card containers
- **Features**: Rounded corners, shadow, padding

#### GameStats.svelte
- **Props**: `score`, `lives`
- **Purpose**: Display game statistics
- **Features**: Heart icons, responsive layout

### Page Components (Svelte 5 Runes)

All pages use **Svelte 5 runes** for state management:

```typescript
// Reactive state
let score = $state(0);
let lives = $state(3);

// Computed values (if needed)
let gameOver = $derived(lives <= 0);

// Effects (if needed)
$effect(() => {
  console.log('Score changed:', score);
});
```

## Database Schema

### Users Collection
```typescript
{
  _id: ObjectId
  name: string
  createdAt: Date
}
```

### Game Sessions Collection
```typescript
{
  _id: ObjectId
  userId: string
  gameType: 'verbal-memory'
  difficulty: 'easy' | 'hard'
  score: number
  lives: number
  wordsShown: string[]
  seenWords: string[]
  isActive: boolean
  startedAt: Date
  endedAt?: Date
}
```

## API Design

### RESTful Principles

- **GET**: Retrieve data (users, stats, individual user)
- **POST**: Create/execute actions (create user, start game, submit answer)
- **DELETE**: Remove data (delete user)

### Routes

**Pages:**
- `/` - Home (user selection, game selection)
- `/game/verbal-memory` - Verbal memory game  
- `/stats/[userId]` - Historical statistics per user

**API:**
- `/api/users` - GET (all), POST (create)
- `/api/users/[id]` - GET (single), DELETE
- `/api/game/verbal-memory/start` - POST
- `/api/game/verbal-memory/answer` - POST
- `/api/game/verbal-memory/stats` - GET (with userId & difficulty params)

### Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad request (validation error)
- `404`: Not found
- `500`: Server error

### Response Format

Consistent JSON responses:
```typescript
// Success
{ ...data }

// Error
{ error: "Error message" }
```

## State Management

### Client State (Svelte 5 Runes)
- `$state()`: Reactive variables
- `$derived()`: Computed values
- `$effect()`: Side effects

### Server State (MongoDB)
- Users
- Game sessions
- Statistics (computed from sessions)

### No Global Store Needed
- State is localized to components
- Data fetched via API as needed
- Simple and maintainable

## Extension Points

### Adding a New Game

1. **Define Types** (`src/lib/types/index.ts`)
   ```typescript
   export type GameType = 'verbal-memory' | 'new-game';
   ```

2. **Create Service** (`src/lib/services/new-game.service.ts`)
   ```typescript
   export class NewGameEngine {
     async startGame(...): Promise<GameState>
     async processInput(...): Promise<GameState>
   }
   ```

3. **Add API Routes** (`src/routes/api/game/new-game/`)
   - `start/+server.ts`
   - `action/+server.ts`
   - `stats/+server.ts`

4. **Create UI** (`src/routes/game/new-game/+page.svelte`)

5. **Update Home** (`src/routes/+page.svelte`)
   - Add game card
   - Add difficulty selection

### Modifying Game Logic

**Example: Change lives from 3 to 5**

File: `src/lib/services/game-engine.service.ts`
```typescript
lives: 5,  // Changed from 3
```

### Adding Statistics

**Example: Track reaction time**

1. Add field to `GameSession` type
2. Update repository save logic
3. Add stats calculation in repository
4. Display in UI

### Customizing Difficulty

**Example: Add "medium" difficulty**

1. Update type: `type DifficultyLevel = 'easy' | 'medium' | 'hard'`
2. Add word pool in `word-pools.ts`
3. Update UI to show 3 buttons

## Performance Considerations

### Database
- Indexes on `userId` and `gameType` for fast queries
- Connection pooling via MongoDB driver
- Singleton pattern for database connection

### Frontend
- Minimal re-renders (Svelte 5 fine-grained reactivity)
- No unnecessary state
- Lazy loading (future: dynamic imports for games)

### API
- Validation at API layer (fast failure)
- Minimal data transfer (only needed fields)

## Security Notes

**⚠️ Current: Local-Only Deployment**

Since this runs locally:
- No authentication required
- Simple user system (name only)
- Direct MongoDB connection

**🔒 For Production (Future):**
- Add authentication (sessions/JWT)
- Validate all inputs
- Rate limiting
- HTTPS
- Environment variables for secrets
- User passwords with hashing

## Testing Strategy (Future)

### Unit Tests
- Services (GameEngine, WordService)
- Repositories (mocked database)
- Pure functions

### Integration Tests
- API endpoints
- Database operations

### E2E Tests
- User flows
- Game completion

## Monitoring & Debugging

### Development
```bash
npm run dev       # Hot reload
npm run check     # Type checking
```

### Database Inspection
```bash
docker exec -it humanbenchmark-mongo mongosh humanbenchmark
db.users.find()
db.game_sessions.find()
```

### Logs
- Server logs: Console output
- MongoDB logs: `docker-compose logs mongodb`

---

## Summary

This architecture prioritizes:
- ✅ **Separation of concerns**: Each layer has one job
- ✅ **Type safety**: TypeScript everywhere
- ✅ **Extensibility**: Easy to add features
- ✅ **Simplicity**: No over-engineering
- ✅ **Kid-friendly**: Large, colorful, intuitive UI
- ✅ **Modern**: Svelte 5, latest patterns
