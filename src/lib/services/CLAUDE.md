---
title: "Services Layer Documentation"
purpose: "Business logic and game engines"
parent: "../../../CLAUDE.md"
last_updated: "2025-10-03"
keywords: ["services", "business-logic", "game-engine", "word-service", "visual-memory", "reaction-time"]
---

# 🎮 Services Layer - Business Logic

**Layer:** Service Layer  
**Location:** `src/lib/services/`  
**Parent Guide:** [Main CLAUDE.md](../../../CLAUDE.md) | [Lib CLAUDE.md](../CLAUDE.md)

---

## 🎯 Purpose

The services layer contains all business logic, game rules, and state management. This layer:
- Implements game mechanics
- Manages game state
- Calculates scores and progression
- Enforces game rules
- **Does NOT** handle database operations directly (uses repositories)

---

## 📂 Files in This Directory

### Game Engines
- **`game-engine.service.ts`** - Verbal memory game logic
- **`visual-memory.service.ts`** - Visual memory game logic  
- **`reaction-time.service.ts`** - Reaction time game logic

### Supporting Services
- **`word.service.ts`** - Word selection for verbal memory

### Test Files
- `game-engine.test.ts` (12 tests)
- `word.service.test.ts` (20 tests)
- `reaction-time.test.ts` (19 tests)

---

## 🎮 Game Engines

### GameEngine (Verbal Memory)

**File:** `game-engine.service.ts`

**Responsibilities:**
- Start new verbal memory game
- Present random words
- Validate user answers (seen/new)
- Track score and lives
- Prevent consecutive duplicate words
- End game when lives reach 0

**Key Methods:**
```typescript
class GameEngine {
  async startGame(userId: string, difficulty: DifficultyLevel): Promise<GameState>
  async submitAnswer(answer: 'seen' | 'new'): Promise<GameState>
  async endGame(): Promise<GameState>
  private nextWord(): string
}
```

**Game Rules:**
- Start with 3 lives
- Correct answer: +1 score, word added to seen list (if new)
- Wrong answer: -1 life
- 50/50 chance of showing new vs. seen word (when seen words available)
- Game ends when lives = 0

**Testing:** 12 unit tests covering game logic, edge cases, no consecutive duplicates

---

### VisualMemoryEngine

**File:** `visual-memory.service.ts`

**Responsibilities:**
- Generate grid patterns (3x3 or 4x4)
- Select random target positions
- Validate user selections
- Track score, lives, and rounds
- Increase difficulty every 2 successful rounds

**Key Methods:**
```typescript
class VisualMemoryEngine {
  async startGame(userId: string, difficulty: DifficultyLevel): Promise<GameState>
  async submitAnswer(userSelections: number[]): Promise<GameState>
  private generateTargets(): number[]
  private validateAnswer(userSelections: number[], targets: number[]): boolean
}
```

**Game Rules:**
- **Easy:** 3x3 grid, start with 2 targets, max 5, 2s presentation, 1s delay
- **Hard:** 4x4 grid, start with 3 targets, max 7, 1.5s presentation, 1.5s delay
- Target count increases every 2 successful rounds
- Order doesn't matter (spatial memory, not sequential)
- Game ends when lives = 0

**Testing:** Manual testing with Playwright

---

### ReactionTimeEngine

**File:** `reaction-time.service.ts`

**Responsibilities:**
- Track reaction times across 5 rounds
- Handle false starts
- Calculate average reaction time
- Store individual round times

**Key Methods:**
```typescript
class ReactionTimeEngine {
  async startGame(userId: string, difficulty: DifficultyLevel): Promise<GameState>
  async submitReaction(reactionTime: number, isFalseStart: boolean): Promise<GameState>
  private calculateAverage(times: number[]): number
}
```

**Game Rules:**
- 5 rounds total
- **Easy:** 2-4 second random delay
- **Hard:** 1-3 second random delay
- False starts increment counter but don't end game
- Score = average reaction time (lower is better)
- Game ends after 5 successful reactions

**Testing:** 19 unit tests

---

## 🔤 Word Service

**File:** `word.service.ts`

**Responsibilities:**
- Initialize word pools by difficulty
- Get random words (excluding recent/seen)
- Select from seen words
- Ensure no immediate duplicates

**Key Methods:**
```typescript
class WordService {
  constructor(difficulty: DifficultyLevel, excludeWords?: string[])
  getRandomWord(): string
  getSeenWord(seenWords: string[], excludeWords?: string[]): string | null
}
```

**Features:**
- Prevents consecutive duplicate words
- Respects exclusion lists
- Returns null if no valid seen words available

**Testing:** 20 unit tests covering randomness, exclusions, edge cases

---

## 🔄 Common Patterns

### Creating a Game Session

```typescript
import { GameEngine } from '$lib/services/game-engine.service';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';

// In API route
const engine = new GameEngine(userId, difficulty);
const gameState = await engine.startGame();

// Engine internally uses repository to persist
```

### Processing Game Actions

```typescript
// Load existing game
const engine = new GameEngine(userId, difficulty);
await engine.loadGame(sessionId);

// Process action
const newState = await engine.submitAnswer('seen');

// Check if game over
if (newState.gameOver) {
  // Handle end game
}
```

---

## 🆕 Adding a New Game Service

### Step-by-Step Guide

1. **Create service file** (`src/lib/services/new-game.service.ts`)

```typescript
import { GameSessionRepository } from '$lib/repositories/game-session.repository';
import type { GameSession, DifficultyLevel } from '$lib/types';

export class NewGameEngine {
  private repository: GameSessionRepository;
  private session: GameSession | null = null;
  
  constructor(
    private userId: string,
    private difficulty: DifficultyLevel
  ) {
    this.repository = new GameSessionRepository();
  }
  
  async startGame(): Promise<GameState> {
    // Create session
    this.session = await this.repository.create({
      userId: this.userId,
      gameType: 'new-game',
      difficulty: this.difficulty,
      score: 0,
      // ... game-specific fields
      isActive: true,
      startedAt: new Date()
    });
    
    // Return initial state
    return {
      sessionId: this.session._id,
      score: 0,
      // ... initial game state
    };
  }
  
  async processAction(action: any): Promise<GameState> {
    if (!this.session) throw new Error('No active session');
    
    // Game logic here
    // Update score, check win/loss conditions
    
    // Persist changes
    await this.repository.update(this.session._id, {
      score: this.session.score,
      // ... updated fields
    });
    
    return {
      sessionId: this.session._id,
      score: this.session.score,
      // ... current state
    };
  }
  
  async endGame(): Promise<GameState> {
    if (!this.session) throw new Error('No active session');
    
    this.session.isActive = false;
    this.session.endedAt = new Date();
    
    await this.repository.update(this.session._id, {
      isActive: false,
      endedAt: this.session.endedAt
    });
    
    return {
      sessionId: this.session._id,
      score: this.session.score,
      gameOver: true,
      message: `Spiel vorbei! Punktzahl: ${this.session.score}`
    };
  }
}
```

2. **Update type definitions** (`src/lib/types/index.ts`)

```typescript
export type GameType = 'verbal-memory' | 'visual-memory' | 'reaction-time' | 'new-game';

export type GameSession = {
  // ... existing fields
  gameType: GameType;
  // Add game-specific fields if needed
  newGameState?: {
    // custom fields
  };
};
```

3. **Create API routes** (`src/routes/api/game/new-game/`)
   - `start/+server.ts`
   - `action/+server.ts`
   - `stats/+server.ts`

4. **Create UI page** (`src/routes/game/new-game/+page.svelte`)

5. **Write tests** (`src/lib/services/new-game.test.ts`)

**See:** [Main CLAUDE.md > Adding a New Game](../../../CLAUDE.md#adding-a-new-game)

---

## 🧪 Testing

### Running Tests

```bash
npm test                        # All tests
npm test game-engine            # Specific file
npm test -- --watch             # Watch mode
npm run test:ui                 # Visual UI
```

### Test Coverage

| Service | Tests | Coverage |
|---------|-------|----------|
| GameEngine | 12 | ✅ Core logic, edge cases, no duplicates |
| WordService | 20 | ✅ Randomness, exclusions, seen words |
| ReactionTimeEngine | 19 | ✅ Timing, false starts, averaging |
| VisualMemoryEngine | Manual | 🧪 Playwright testing |

### Writing New Tests

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { NewGameEngine } from './new-game.service';

describe('NewGameEngine', () => {
  let engine: NewGameEngine;
  
  beforeEach(() => {
    engine = new NewGameEngine('user-id', 'easy');
  });
  
  it('should start game with initial state', async () => {
    const state = await engine.startGame();
    expect(state.score).toBe(0);
    expect(state.sessionId).toBeDefined();
  });
  
  it('should process action correctly', async () => {
    await engine.startGame();
    const state = await engine.processAction({ /* action */ });
    expect(state.score).toBeGreaterThan(0);
  });
});
```

---

## 🔒 Best Practices

### DO ✅
- Keep business logic in services
- Use repositories for data access
- Write unit tests for game logic
- Return consistent state objects
- Handle errors gracefully
- Validate inputs

### DON'T ❌
- Access MongoDB directly from services
- Put UI logic in services
- Ignore error cases
- Mutate input parameters
- Skip testing edge cases

---

## 🐛 Common Issues

### Issue: Service tests failing
**Solution:** Mock repository methods, don't use real database

### Issue: Game state not persisting
**Solution:** Ensure repository.update() is called after state changes

### Issue: Duplicate words appearing
**Solution:** Check excludeWords array includes previous word

**See:** [TROUBLESHOOTING.md](../../../TROUBLESHOOTING.md)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../../CLAUDE.md) - Entry point
- [ARCHITECTURE.md](../../../ARCHITECTURE.md#service-layer-pattern) - Service layer design
- [Lib CLAUDE.md](../CLAUDE.md) - Lib layer overview
- [repositories/CLAUDE.md](../repositories/CLAUDE.md) - Data access layer
- [src/routes/api/CLAUDE.md](../../routes/api/CLAUDE.md) - How services are used in APIs

---

**For adding new games or modifying existing game logic, this is your primary workspace.**

