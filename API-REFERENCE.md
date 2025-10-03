# 📡 API Reference

**Purpose:** Complete reference for all API endpoints.  
**Related Docs:** [AI-GUIDE.md](./AI-GUIDE.md) | [ARCHITECTURE.md](./ARCHITECTURE.md)

**Base URL:** `http://localhost:5173/api` (development)

---

## Table of Contents

- [User Management](#user-management)
  - [GET /users](#get-users)
  - [POST /users](#post-users)
  - [GET /users/:id](#get-usersid)
  - [DELETE /users/:id](#delete-usersid)
- [Verbal Memory Game](#verbal-memory-game)
  - [POST /game/verbal-memory/start](#post-gameverbal-memorystart)
  - [POST /game/verbal-memory/answer](#post-gameverbal-memoryanswer)
  - [GET /game/verbal-memory/stats](#get-gameverbal-memorystats)

---

## User Management

### GET /users

Get all users in the system.

**Endpoint:** `/api/users`  
**Method:** `GET`  
**Authentication:** None

**Request:**
```http
GET /api/users HTTP/1.1
```

**Response:** `200 OK`
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "name": "Max",
    "createdAt": "2025-01-03T12:00:00.000Z"
  },
  {
    "_id": "507f1f77bcf86cd799439012",
    "name": "Emma",
    "createdAt": "2025-01-03T12:05:00.000Z"
  }
]
```

**Response Fields:**
- `_id` (string): Unique user identifier (MongoDB ObjectId)
- `name` (string): User's display name
- `createdAt` (string): ISO 8601 timestamp of user creation

**Errors:**
- None (returns empty array if no users)

**Example Usage:**
```typescript
const response = await fetch('/api/users');
const users = await response.json();
```

**File:** `src/routes/api/users/+server.ts`

---

### POST /users

Create a new user.

**Endpoint:** `/api/users`  
**Method:** `POST`  
**Authentication:** None

**Request:**
```http
POST /api/users HTTP/1.1
Content-Type: application/json

{
  "name": "Max"
}
```

**Request Body:**
- `name` (string, required): User's display name

**Response:** `201 Created`
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Max",
  "createdAt": "2025-01-03T12:00:00.000Z"
}
```

**Response Fields:**
- `_id` (string): Unique user identifier
- `name` (string): User's display name
- `createdAt` (string): ISO 8601 timestamp

**Errors:**

**400 Bad Request** - Invalid or missing name
```json
{
  "error": "Name is required"
}
```

**Example Usage:**
```typescript
const response = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Max' })
});
const user = await response.json();
```

**Validation:**
- Name must be non-empty string
- Name is trimmed before saving
- Duplicate names are allowed

**File:** `src/routes/api/users/+server.ts`

---

### GET /users/:id

Get a specific user by ID.

**Endpoint:** `/api/users/:id`  
**Method:** `GET`  
**Authentication:** None

**URL Parameters:**
- `id` (string, required): User's MongoDB ObjectId

**Request:**
```http
GET /api/users/507f1f77bcf86cd799439011 HTTP/1.1
```

**Response:** `200 OK`
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Max",
  "createdAt": "2025-01-03T12:00:00.000Z"
}
```

**Errors:**

**404 Not Found** - User doesn't exist
```json
{
  "error": "User not found"
}
```

**400 Bad Request** - Invalid ObjectId format
```json
{
  "error": "Invalid ID"
}
```

**Example Usage:**
```typescript
const response = await fetch(`/api/users/${userId}`);
if (response.ok) {
  const user = await response.json();
}
```

**File:** `src/routes/api/users/[id]/+server.ts`

---

### DELETE /users/:id

Delete a user.

**Endpoint:** `/api/users/:id`  
**Method:** `DELETE`  
**Authentication:** None

**URL Parameters:**
- `id` (string, required): User's MongoDB ObjectId

**Request:**
```http
DELETE /api/users/507f1f77bcf86cd799439011 HTTP/1.1
```

**Response:** `200 OK`
```json
{
  "success": true
}
```

**Errors:**

**404 Not Found** - User doesn't exist
```json
{
  "error": "User not found"
}
```

**Note:** This does NOT delete associated game sessions (orphaned data will remain).

**Example Usage:**
```typescript
const response = await fetch(`/api/users/${userId}`, {
  method: 'DELETE'
});
```

**File:** `src/routes/api/users/[id]/+server.ts`

---

## Verbal Memory Game

### POST /game/verbal-memory/start

Start a new verbal memory game session.

**Endpoint:** `/api/game/verbal-memory/start`  
**Method:** `POST`  
**Authentication:** None

**Request:**
```http
POST /api/game/verbal-memory/start HTTP/1.1
Content-Type: application/json

{
  "userId": "507f1f77bcf86cd799439011",
  "difficulty": "easy"
}
```

**Request Body:**
- `userId` (string, required): User's MongoDB ObjectId
- `difficulty` (string, required): Either "easy" or "hard"

**Response:** `200 OK`
```json
{
  "sessionId": "507f1f77bcf86cd799439020",
  "currentWord": "Hund",
  "score": 0,
  "lives": 3
}
```

**Response Fields:**
- `sessionId` (string): Unique game session identifier
- `currentWord` (string): First word to display
- `score` (number): Current score (always 0 at start)
- `lives` (number): Remaining lives (always 3 at start)

**Errors:**

**400 Bad Request** - Missing required fields
```json
{
  "error": "userId and difficulty are required"
}
```

**400 Bad Request** - Invalid difficulty
```json
{
  "error": "difficulty must be \"easy\" or \"hard\""
}
```

**Game Rules:**
- **Easy Mode:** Uses 70 simple German words (animals, colors, food, etc.)
- **Hard Mode:** Uses 75 complex words (compound words, actions, places)
- Starts with 3 lives
- First word is always new
- Score increases by 1 for correct answers
- Lives decrease by 1 for incorrect answers

**Example Usage:**
```typescript
const response = await fetch('/api/game/verbal-memory/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    userId: user._id,
    difficulty: 'easy'
  })
});
const gameState = await response.json();
```

**File:** `src/routes/api/game/verbal-memory/start/+server.ts`

---

### POST /game/verbal-memory/answer

Submit an answer for the current word.

**Endpoint:** `/api/game/verbal-memory/answer`  
**Method:** `POST`  
**Authentication:** None

**Request:**
```http
POST /api/game/verbal-memory/answer HTTP/1.1
Content-Type: application/json

{
  "sessionId": "507f1f77bcf86cd799439020",
  "answer": "new"
}
```

**Request Body:**
- `sessionId` (string, required): Game session identifier
- `answer` (string, required): Either "new" or "seen"

**Response:** `200 OK`

**If game continues:**
```json
{
  "currentWord": "Katze",
  "score": 1,
  "lives": 3,
  "gameOver": false,
  "message": null
}
```

**If game over:**
```json
{
  "currentWord": null,
  "score": 5,
  "lives": 0,
  "gameOver": true,
  "message": "Spiel vorbei! Deine Punktzahl: 5"
}
```

**Response Fields:**
- `currentWord` (string|null): Next word to display (null if game over)
- `score` (number): Updated score
- `lives` (number): Remaining lives
- `gameOver` (boolean): Whether the game has ended
- `message` (string|null): Game over message

**Errors:**

**400 Bad Request** - Missing fields
```json
{
  "error": "sessionId and answer are required"
}
```

**400 Bad Request** - Invalid answer
```json
{
  "error": "answer must be \"seen\" or \"new\""
}
```

**Game Logic:**
1. Check if answer matches actual word state
2. If correct: increment score, add word to seen list if new
3. If incorrect: decrement lives
4. If lives > 0: generate next word
5. If lives = 0: end game
6. 50/50 chance of showing new vs. seen word (if seen words available)

**Example Usage:**
```typescript
const response = await fetch('/api/game/verbal-memory/answer', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sessionId: currentSessionId,
    answer: 'new'
  })
});
const gameState = await response.json();

if (gameState.gameOver) {
  // Show game over screen
} else {
  // Show next word
}
```

**File:** `src/routes/api/game/verbal-memory/answer/+server.ts`

---

### GET /game/verbal-memory/stats

Get statistics for a user's verbal memory games.

**Endpoint:** `/api/game/verbal-memory/stats`  
**Method:** `GET`  
**Authentication:** None

**Query Parameters:**
- `userId` (string, required): User's MongoDB ObjectId
- `difficulty` (string, required): Either "easy" or "hard"

**Request:**
```http
GET /api/game/verbal-memory/stats?userId=507f1f77bcf86cd799439011&difficulty=easy HTTP/1.1
```

**Response:** `200 OK`
```json
{
  "totalGames": 5,
  "highScore": 12,
  "averageScore": 8,
  "lastPlayed": "2025-01-03T14:30:00.000Z"
}
```

**Response Fields:**
- `totalGames` (number): Number of completed games
- `highScore` (number): Best score achieved
- `averageScore` (number): Average score (rounded)
- `lastPlayed` (string|undefined): ISO 8601 timestamp of last game

**Empty State:**
If user has no games:
```json
{
  "totalGames": 0,
  "highScore": 0,
  "averageScore": 0
}
```

**Errors:**

**400 Bad Request** - Missing parameters
```json
{
  "error": "userId and difficulty are required"
}
```

**Notes:**
- Only counts completed games (where `isActive = false`)
- Stats are calculated per difficulty level
- Active games are not included in statistics

**Example Usage:**
```typescript
const response = await fetch(
  `/api/game/verbal-memory/stats?userId=${userId}&difficulty=easy`
);
const stats = await response.json();
console.log(`High score: ${stats.highScore}`);
```

**File:** `src/routes/api/game/verbal-memory/stats/+server.ts`

---

## Common Patterns

### Error Handling

All endpoints return errors in this format:
```json
{
  "error": "Error message"
}
```

With appropriate HTTP status codes:
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

### Request Headers

Always include for POST requests:
```http
Content-Type: application/json
```

### Response Format

All responses are JSON with:
```http
Content-Type: application/json
```

### MongoDB ObjectIds

- Always 24 character hex strings
- Example: `507f1f77bcf86cd799439011`
- Invalid formats return 400 error

---

## Rate Limiting

**Current:** None  
**Future:** Consider adding for production deployment

---

## CORS

**Current:** None (same-origin only)  
**Future:** Configure for production if needed

---

## Versioning

**Current:** No API versioning  
**Future:** Consider `/api/v1/` prefix before breaking changes

---

## Testing

### Manual Testing with curl

**Create User:**
```bash
curl -X POST http://localhost:5173/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"TestUser"}'
```

**Get Users:**
```bash
curl http://localhost:5173/api/users
```

**Start Game:**
```bash
curl -X POST http://localhost:5173/api/game/verbal-memory/start \
  -H "Content-Type: application/json" \
  -d '{"userId":"507f1f77bcf86cd799439011","difficulty":"easy"}'
```

**Submit Answer:**
```bash
curl -X POST http://localhost:5173/api/game/verbal-memory/answer \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"507f1f77bcf86cd799439020","answer":"new"}'
```

**Get Stats:**
```bash
curl "http://localhost:5173/api/game/verbal-memory/stats?userId=507f1f77bcf86cd799439011&difficulty=easy"
```

---

## Future Endpoints

### Planned (Not Yet Implemented)

**Game Management:**
- `GET /game/sessions/:id` - Get session details
- `DELETE /game/sessions/:id` - Delete session

**User Profile:**
- `PATCH /users/:id` - Update user name
- `GET /users/:id/stats` - Get all stats for user

**Leaderboard:**
- `GET /game/verbal-memory/leaderboard` - Get top scores

**New Games:**
- `POST /game/reaction-time/start`
- `POST /game/number-memory/start`

---

## Implementation Details

### Database Operations

Each endpoint:
1. Calls `connectToDatabase()` at start
2. Uses repository classes for data access
3. Returns JSON responses
4. Handles errors with try/catch

### Service Layer

Game endpoints use:
- `GameEngine` for game state management
- `WordService` for word selection
- `GameSessionRepository` for persistence

### Type Safety

All endpoints have TypeScript types via:
```typescript
import type { RequestHandler } from './$types';
```

---

**Related Documentation:**
- [AI-GUIDE.md](./AI-GUIDE.md) - Overall guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
