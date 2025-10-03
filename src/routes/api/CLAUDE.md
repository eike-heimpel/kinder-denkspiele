---
title: "API Layer Documentation"
purpose: "Backend API endpoints - request handlers and business logic coordination"
parent: "../../../CLAUDE.md"
last_updated: "2025-10-03"
keywords: ["api", "endpoints", "server", "backend", "rest", "http"]
---

# 🔌 API Layer - Backend Endpoints

**Layer:** API Layer  
**Location:** `src/routes/api/`  
**Parent Guide:** [Main CLAUDE.md](../../../CLAUDE.md) | [Routes CLAUDE.md](../CLAUDE.md)

---

## 🎯 Purpose

API endpoints handle backend operations:
- Receive HTTP requests
- Validate inputs
- Call services for business logic
- Return JSON responses
- Handle errors gracefully

---

## 📂 Directory Structure

```
src/routes/api/
├── users/
│   ├── +server.ts          # GET, POST /api/users
│   └── [id]/
│       └── +server.ts      # GET, DELETE /api/users/:id
│
└── game/
    ├── verbal-memory/
    │   ├── start/+server.ts     # Start game
    │   ├── answer/+server.ts    # Submit answer
    │   └── stats/+server.ts     # Get statistics
    │
    ├── visual-memory/
    │   ├── start/+server.ts
    │   ├── answer/+server.ts
    │   └── stats/+server.ts
    │
    └── reaction-time/
        ├── start/+server.ts
        ├── submit/+server.ts
        └── stats/+server.ts
```

---

## 👥 User Management API

### GET /api/users

Get all users.

**File:** `users/+server.ts`

```typescript
export const GET: RequestHandler = async () => {
  try {
    const userRepo = new UserRepository();
    const users = await userRepo.findAll();
    return json(users);
  } catch (error) {
    return json({ error: 'Failed to fetch users' }, { status: 500 });
  }
};
```

**Response:** `User[]`

---

### POST /api/users

Create new user.

**File:** `users/+server.ts`

```typescript
export const POST: RequestHandler = async ({ request }) => {
  try {
    const { name } = await request.json();
    
    if (!name || typeof name !== 'string' || !name.trim()) {
      return json({ error: 'Name is required' }, { status: 400 });
    }
    
    const userRepo = new UserRepository();
    const user = await userRepo.create(name.trim());
    
    return json(user, { status: 201 });
  } catch (error) {
    return json({ error: 'Failed to create user' }, { status: 500 });
  }
};
```

**Request Body:** `{ name: string }`  
**Response:** `User` (201)

---

### GET /api/users/[id]

Get user by ID.

**File:** `users/[id]/+server.ts`

```typescript
export const GET: RequestHandler = async ({ params }) => {
  try {
    const userRepo = new UserRepository();
    const user = await userRepo.findById(params.id);
    
    if (!user) {
      return json({ error: 'User not found' }, { status: 404 });
    }
    
    return json(user);
  } catch (error) {
    return json({ error: 'Failed to fetch user' }, { status: 500 });
  }
};
```

**Response:** `User` or 404

---

### DELETE /api/users/[id]

Delete user.

**File:** `users/[id]/+server.ts`

```typescript
export const DELETE: RequestHandler = async ({ params }) => {
  try {
    const userRepo = new UserRepository();
    const success = await userRepo.delete(params.id);
    
    if (!success) {
      return json({ error: 'User not found' }, { status: 404 });
    }
    
    return json({ success: true });
  } catch (error) {
    return json({ error: 'Failed to delete user' }, { status: 500 });
  }
};
```

**Response:** `{ success: true }` or 404

---

## 🎮 Game API

### Verbal Memory

**Directory:** `game/verbal-memory/`

#### POST /api/game/verbal-memory/start

Start new game.

**File:** `start/+server.ts`

```typescript
export const POST: RequestHandler = async ({ request }) => {
  try {
    const { userId, difficulty } = await request.json();
    
    if (!userId || !difficulty) {
      return json(
        { error: 'userId and difficulty are required' },
        { status: 400 }
      );
    }
    
    if (difficulty !== 'easy' && difficulty !== 'hard') {
      return json(
        { error: 'difficulty must be "easy" or "hard"' },
        { status: 400 }
      );
    }
    
    const engine = new GameEngine(userId, difficulty);
    const state = await engine.startGame();
    
    return json(state);
  } catch (error) {
    return json({ error: 'Failed to start game' }, { status: 500 });
  }
};
```

**Request:** `{ userId: string, difficulty: 'easy' | 'hard' }`  
**Response:** `{ sessionId, currentWord, score, lives }`

---

#### POST /api/game/verbal-memory/answer

Submit answer.

**File:** `answer/+server.ts`

```typescript
export const POST: RequestHandler = async ({ request }) => {
  try {
    const { sessionId, answer } = await request.json();
    
    if (!sessionId || !answer) {
      return json(
        { error: 'sessionId and answer are required' },
        { status: 400 }
      );
    }
    
    if (answer !== 'seen' && answer !== 'new') {
      return json(
        { error: 'answer must be "seen" or "new"' },
        { status: 400 }
      );
    }
    
    const engine = new GameEngine('', '');
    await engine.loadGame(sessionId);
    const state = await engine.submitAnswer(answer);
    
    return json(state);
  } catch (error) {
    return json({ error: 'Failed to submit answer' }, { status: 500 });
  }
};
```

**Request:** `{ sessionId: string, answer: 'seen' | 'new' }`  
**Response:** `{ currentWord, score, lives, gameOver, message? }`

---

#### GET /api/game/verbal-memory/stats

Get statistics.

**File:** `stats/+server.ts`

```typescript
export const GET: RequestHandler = async ({ url }) => {
  try {
    const userId = url.searchParams.get('userId');
    const difficulty = url.searchParams.get('difficulty');
    
    if (!userId || !difficulty) {
      return json(
        { error: 'userId and difficulty are required' },
        { status: 400 }
      );
    }
    
    const sessionRepo = new GameSessionRepository();
    const stats = await sessionRepo.getStats(
      userId,
      'verbal-memory',
      difficulty as DifficultyLevel
    );
    
    return json(stats);
  } catch (error) {
    return json({ error: 'Failed to fetch stats' }, { status: 500 });
  }
};
```

**Query Params:** `?userId=X&difficulty=Y`  
**Response:** `{ totalGames, highScore, averageScore, lastPlayed? }`

---

### Visual Memory & Reaction Time

Similar structure to Verbal Memory:

**Visual Memory:**
- `POST /api/game/visual-memory/start`
- `POST /api/game/visual-memory/answer`
- `GET /api/game/visual-memory/stats`

**Reaction Time:**
- `POST /api/game/reaction-time/start`
- `POST /api/game/reaction-time/submit`
- `GET /api/game/reaction-time/stats`

**See:** [API-REFERENCE.md](../../../API-REFERENCE.md) for complete API documentation

---

## 🔄 Common Patterns

### Standard Endpoint Structure

```typescript
import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';
import { ServiceClass } from '$lib/services/service.service';

export const POST: RequestHandler = async ({ request }) => {
  try {
    // 1. Parse request body
    const body = await request.json();
    
    // 2. Validate inputs
    if (!body.requiredField) {
      return json({ error: 'Field required' }, { status: 400 });
    }
    
    // 3. Call service layer
    const service = new ServiceClass();
    const result = await service.doSomething(body);
    
    // 4. Return response
    return json(result);
  } catch (error) {
    // 5. Handle errors
    console.error(error);
    return json({ error: 'Operation failed' }, { status: 500 });
  }
};
```

### Query Parameters

```typescript
export const GET: RequestHandler = async ({ url }) => {
  const param1 = url.searchParams.get('param1');
  const param2 = url.searchParams.get('param2');
  
  if (!param1) {
    return json({ error: 'param1 required' }, { status: 400 });
  }
  
  // Use params...
};
```

### Dynamic Route Parameters

```typescript
export const GET: RequestHandler = async ({ params }) => {
  const id = params.id;  // From /api/users/[id]
  
  // Use id...
};
```

---

## 🆕 Adding New Endpoints

### Step-by-Step

1. **Create directory structure**

```
src/routes/api/new-endpoint/
└── +server.ts
```

2. **Implement handler**

```typescript
import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  return json({ message: 'Hello' });
};

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();
  
  // Validate
  if (!body.field) {
    return json({ error: 'field required' }, { status: 400 });
  }
  
  // Process
  // ...
  
  return json({ success: true });
};
```

3. **Test endpoint**

```bash
curl http://localhost:5173/api/new-endpoint
curl -X POST http://localhost:5173/api/new-endpoint \
  -H "Content-Type: application/json" \
  -d '{"field":"value"}'
```

---

## ✅ Validation Patterns

### Required Fields

```typescript
const { field1, field2 } = await request.json();

if (!field1 || !field2) {
  return json(
    { error: 'field1 and field2 are required' },
    { status: 400 }
  );
}
```

### Type Validation

```typescript
if (typeof name !== 'string' || !name.trim()) {
  return json({ error: 'name must be non-empty string' }, { status: 400 });
}
```

### Enum Validation

```typescript
if (difficulty !== 'easy' && difficulty !== 'hard') {
  return json(
    { error: 'difficulty must be "easy" or "hard"' },
    { status: 400 }
  );
}
```

### ObjectId Validation

```typescript
import { ObjectId } from 'mongodb';

if (!ObjectId.isValid(id)) {
  return json({ error: 'Invalid ID format' }, { status: 400 });
}
```

---

## 📊 HTTP Status Codes

Use appropriate status codes:

| Code | Usage |
|------|-------|
| 200 | Success (GET, PUT, DELETE) |
| 201 | Created (POST) |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Internal Server Error |

```typescript
// Success
return json(data);  // Default 200

// Created
return json(data, { status: 201 });

// Bad Request
return json({ error: 'Invalid input' }, { status: 400 });

// Not Found
return json({ error: 'Not found' }, { status: 404 });

// Server Error
return json({ error: 'Server error' }, { status: 500 });
```

---

## 🔒 Best Practices

### DO ✅
- Validate all inputs
- Return consistent JSON responses
- Use appropriate HTTP status codes
- Handle errors with try/catch
- Log errors (console.error)
- Keep endpoints focused (single responsibility)

### DON'T ❌
- Put business logic in API handlers (use services)
- Access database directly (use repositories via services)
- Return different response formats
- Expose internal error details to client
- Skip input validation

---

## 🧪 Testing APIs

### Manual Testing with curl

```bash
# Create user
curl -X POST http://localhost:5173/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"TestUser"}'

# Get users
curl http://localhost:5173/api/users

# Start game
curl -X POST http://localhost:5173/api/game/verbal-memory/start \
  -H "Content-Type: application/json" \
  -d '{"userId":"507f...","difficulty":"easy"}'
```

### From Frontend

```typescript
// GET
const response = await fetch('/api/users');
const users = await response.json();

// POST
const response = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Max' })
});
const user = await response.json();
```

**See:** [API-REFERENCE.md](../../../API-REFERENCE.md#testing) for more examples

---

## 🐛 Common Issues

### Issue: "Cannot read property 'json' of undefined"
**Solution:** Ensure request body is being sent with Content-Type: application/json

### Issue: CORS errors
**Solution:** Not needed for same-origin (SvelteKit handles this)

### Issue: 404 on API endpoint
**Solution:** Check file is named `+server.ts` and in correct directory

**See:** [TROUBLESHOOTING.md](../../../TROUBLESHOOTING.md)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../../CLAUDE.md) - Entry point
- [Routes CLAUDE.md](../CLAUDE.md) - Routing overview
- [API-REFERENCE.md](../../../API-REFERENCE.md) - Complete API specs
- [services/CLAUDE.md](../../lib/services/CLAUDE.md) - Business logic layer
- [ARCHITECTURE.md](../../../ARCHITECTURE.md#api-layer) - API design

---

**API endpoints are the bridge between frontend UI and backend services. Keep them thin and focused on request/response handling.**

