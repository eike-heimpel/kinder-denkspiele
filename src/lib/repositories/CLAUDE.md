---
title: "Repositories Layer Documentation"
purpose: "Data access layer - CRUD operations for MongoDB"
parent: "../../../CLAUDE.md"
last_updated: "2025-10-03"
keywords: ["repositories", "data-access", "mongodb", "crud", "persistence", "database"]
---

# 💾 Repositories Layer - Data Access

**Layer:** Repository Layer  
**Location:** `src/lib/repositories/`  
**Parent Guide:** [Main CLAUDE.md](../../../CLAUDE.md) | [Lib CLAUDE.md](../CLAUDE.md)

---

## 🎯 Purpose

The repository layer abstracts all database operations, providing a clean API for data access. This layer:
- Performs CRUD operations (Create, Read, Update, Delete)
- Connects to MongoDB
- Handles data transformation
- Provides query methods
- **Does NOT** contain business logic (that's in services)

---

## 📂 Files in This Directory

- **`user.repository.ts`** - User management (create, read, delete users)
- **`game-session.repository.ts`** - Game session persistence and statistics

---

## 👤 UserRepository

**File:** `user.repository.ts`

Manages user data in the `users` collection.

### Methods

```typescript
class UserRepository {
  // Create a new user
  async create(name: string): Promise<User>
  
  // Get all users
  async findAll(): Promise<User[]>
  
  // Get user by ID
  async findById(id: string): Promise<User | null>
  
  // Delete user by ID
  async delete(id: string): Promise<boolean>
}
```

### Usage Examples

**Create User:**
```typescript
import { UserRepository } from '$lib/repositories/user.repository';

const userRepo = new UserRepository();
const user = await userRepo.create('Max');

console.log(user);
// {
//   _id: '507f1f77bcf86cd799439011',
//   name: 'Max',
//   createdAt: Date
// }
```

**Find All Users:**
```typescript
const users = await userRepo.findAll();
// Returns User[] sorted by createdAt DESC
```

**Find User by ID:**
```typescript
const user = await userRepo.findById('507f1f77bcf86cd799439011');
// Returns User | null
```

**Delete User:**
```typescript
const success = await userRepo.delete('507f1f77bcf86cd799439011');
// Returns true if deleted, false if not found
```

### Database Schema

```typescript
// users collection
{
  _id: ObjectId
  name: string
  createdAt: Date
}
```

**Note:** Deleting a user does NOT cascade delete their game sessions (orphaned data will remain).

---

## 🎮 GameSessionRepository

**File:** `game-session.repository.ts`

Manages game sessions in the `game_sessions` collection.

### Methods

```typescript
class GameSessionRepository {
  // Create new game session
  async create(session: Partial<GameSession>): Promise<GameSession>
  
  // Find session by ID
  async findById(id: string): Promise<GameSession | null>
  
  // Update session
  async update(id: string, updates: Partial<GameSession>): Promise<boolean>
  
  // Get statistics for a user and game type
  async getStats(
    userId: string,
    gameType: GameType,
    difficulty?: DifficultyLevel
  ): Promise<GameStats>
  
  // Get all sessions for a user (for stats page)
  async findByUserId(userId: string): Promise<GameSession[]>
}
```

### Usage Examples

**Create Session:**
```typescript
import { GameSessionRepository } from '$lib/repositories/game-session.repository';

const sessionRepo = new GameSessionRepository();
const session = await sessionRepo.create({
  userId: '507f1f77bcf86cd799439011',
  gameType: 'verbal-memory',
  difficulty: 'easy',
  score: 0,
  lives: 3,
  wordsShown: [],
  seenWords: [],
  isActive: true,
  startedAt: new Date()
});
```

**Update Session:**
```typescript
await sessionRepo.update(sessionId, {
  score: 5,
  lives: 2,
  wordsShown: ['Hund', 'Katze', 'Baum'],
  seenWords: ['Hund']
});
```

**End Session:**
```typescript
await sessionRepo.update(sessionId, {
  isActive: false,
  endedAt: new Date()
});
```

**Get Statistics:**
```typescript
const stats = await sessionRepo.getStats(
  userId,
  'verbal-memory',
  'easy'
);

console.log(stats);
// {
//   totalGames: 5,
//   highScore: 12,
//   averageScore: 8,
//   lastPlayed: Date
// }
```

**Get All User Sessions:**
```typescript
const sessions = await sessionRepo.findByUserId(userId);
// Returns all sessions for stats page
```

### Database Schema

```typescript
// game_sessions collection
{
  _id: ObjectId
  userId: string
  gameType: 'verbal-memory' | 'visual-memory' | 'reaction-time'
  difficulty: 'easy' | 'hard'
  score: number
  lives: number
  round: number
  isActive: boolean
  startedAt: Date
  endedAt?: Date
  
  // Game-specific fields
  wordsShown?: string[]           // Verbal memory
  seenWords?: string[]            // Verbal memory
  visualMemoryState?: { ... }     // Visual memory
  reactionTimeState?: { ... }     // Reaction time
}
```

---

## 🗄️ Database Connection

All repositories use the MongoDB singleton client.

### Pattern

```typescript
import { connectToDatabase } from '$lib/db/client';
import type { User } from '$lib/types';

export class UserRepository {
  async findAll(): Promise<User[]> {
    const db = await connectToDatabase();
    const collection = db.collection<User>('users');
    
    const users = await collection
      .find()
      .sort({ createdAt: -1 })
      .toArray();
    
    return users.map(user => ({
      ...user,
      _id: user._id.toString()
    }));
  }
}
```

### Key Points

- Always call `connectToDatabase()` at the start of each method
- Connection is pooled and reused (singleton pattern)
- Transform `ObjectId` to string for API responses
- Use TypeScript generics for type safety

---

## 🆕 Adding a New Repository

### Step-by-Step

1. **Create repository file** (`src/lib/repositories/new.repository.ts`)

```typescript
import { connectToDatabase } from '$lib/db/client';
import { ObjectId } from 'mongodb';
import type { NewType } from '$lib/types';

export class NewRepository {
  private collectionName = 'new_collection';
  
  async create(data: Partial<NewType>): Promise<NewType> {
    const db = await connectToDatabase();
    const collection = db.collection(this.collectionName);
    
    const result = await collection.insertOne({
      ...data,
      createdAt: new Date()
    });
    
    return {
      _id: result.insertedId.toString(),
      ...data,
      createdAt: new Date()
    } as NewType;
  }
  
  async findById(id: string): Promise<NewType | null> {
    const db = await connectToDatabase();
    const collection = db.collection<NewType>(this.collectionName);
    
    const item = await collection.findOne({
      _id: new ObjectId(id)
    });
    
    if (!item) return null;
    
    return {
      ...item,
      _id: item._id.toString()
    };
  }
  
  async update(id: string, updates: Partial<NewType>): Promise<boolean> {
    const db = await connectToDatabase();
    const collection = db.collection(this.collectionName);
    
    const result = await collection.updateOne(
      { _id: new ObjectId(id) },
      { $set: updates }
    );
    
    return result.modifiedCount > 0;
  }
  
  async delete(id: string): Promise<boolean> {
    const db = await connectToDatabase();
    const collection = db.collection(this.collectionName);
    
    const result = await collection.deleteOne({
      _id: new ObjectId(id)
    });
    
    return result.deletedCount > 0;
  }
}
```

2. **Define types** (`src/lib/types/index.ts`)

```typescript
export type NewType = {
  _id: string;
  // ... fields
  createdAt: Date;
  updatedAt?: Date;
};
```

3. **Use in services**

```typescript
import { NewRepository } from '$lib/repositories/new.repository';

export class NewService {
  private repository: NewRepository;
  
  constructor() {
    this.repository = new NewRepository();
  }
  
  async doSomething() {
    const item = await this.repository.create({ /* ... */ });
    // Business logic here
  }
}
```

---

## 🔄 Common Patterns

### Query with Filters

```typescript
async findByType(gameType: GameType): Promise<GameSession[]> {
  const db = await connectToDatabase();
  const collection = db.collection<GameSession>('game_sessions');
  
  return await collection
    .find({ gameType })
    .sort({ startedAt: -1 })
    .toArray();
}
```

### Aggregation Pipeline

```typescript
async getStats(userId: string, gameType: GameType): Promise<Stats> {
  const db = await connectToDatabase();
  const collection = db.collection('game_sessions');
  
  const result = await collection.aggregate([
    {
      $match: {
        userId,
        gameType,
        isActive: false
      }
    },
    {
      $group: {
        _id: null,
        totalGames: { $sum: 1 },
        highScore: { $max: '$score' },
        avgScore: { $avg: '$score' }
      }
    }
  ]).toArray();
  
  return result[0] || { totalGames: 0, highScore: 0, avgScore: 0 };
}
```

### Batch Operations

```typescript
async createMany(items: NewType[]): Promise<void> {
  const db = await connectToDatabase();
  const collection = db.collection(this.collectionName);
  
  await collection.insertMany(items);
}
```

---

## 🧪 Testing

### Mocking Repositories in Tests

```typescript
import { describe, it, expect, vi } from 'vitest';
import { GameEngine } from '$lib/services/game-engine.service';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';

// Mock the repository
vi.mock('$lib/repositories/game-session.repository', () => ({
  GameSessionRepository: vi.fn().mockImplementation(() => ({
    create: vi.fn().mockResolvedValue({
      _id: 'test-id',
      score: 0,
      lives: 3
    }),
    update: vi.fn().mockResolvedValue(true)
  }))
}));

describe('GameEngine', () => {
  it('should start game', async () => {
    const engine = new GameEngine('user-id', 'easy');
    const state = await engine.startGame();
    
    expect(state.score).toBe(0);
  });
});
```

**Note:** Most repository methods are integration-tested through service tests.

---

## 🔒 Best Practices

### DO ✅
- Always transform `ObjectId` to string in responses
- Use TypeScript types for collections
- Handle null/undefined returns
- Use indexes for frequently queried fields
- Validate ObjectId format before querying
- Close cursors after iteration

### DON'T ❌
- Put business logic in repositories
- Return MongoDB-specific objects directly
- Forget to handle connection errors
- Use string concatenation for queries (use filters)
- Expose internal database structure

---

## 🐛 Common Issues

### Issue: "Cannot read property '_id' of null"
**Solution:** Check if document exists before accessing properties

```typescript
const item = await collection.findOne({ _id: new ObjectId(id) });
if (!item) return null;
return item;
```

### Issue: "Invalid ObjectId format"
**Solution:** Validate ID before creating ObjectId

```typescript
import { ObjectId } from 'mongodb';

if (!ObjectId.isValid(id)) {
  throw new Error('Invalid ID format');
}
```

### Issue: Connection timeouts
**Solution:** Check MongoDB is running and `MONGODB_URI` is set

```bash
docker-compose up -d
echo $MONGODB_URI
```

**See:** [TROUBLESHOOTING.md > MongoDB](../../../TROUBLESHOOTING.md#mongodb-connection-failed)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../../CLAUDE.md) - Entry point
- [Lib CLAUDE.md](../CLAUDE.md) - Lib layer overview
- [ARCHITECTURE.md](../../../ARCHITECTURE.md#repository-pattern) - Repository pattern
- [services/CLAUDE.md](../services/CLAUDE.md) - How repositories are used
- [src/routes/api/CLAUDE.md](../../routes/api/CLAUDE.md) - API usage

---

**Repositories are the ONLY layer that should directly interact with MongoDB.**

