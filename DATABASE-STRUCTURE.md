# Database Structure Documentation

**Last Updated:** 2025-11-05
**Purpose:** Document the actual database structure, collections, and relationships across all MongoDB databases used by this project.

---

## Overview

This project uses **MongoDB Atlas** with multiple databases. The connection string is stored in the `.env` file as `MONGODB_URI`.

---

## Database List

The MongoDB cluster contains these databases:

1. **humanbenchmark** - Main application database
2. **myFirstDatabase** - User authentication database
3. **mongodb** - Unrelated project (story creation tool)
4. **gameDatabase** - Unrelated game data
5. **forge**, **forge-test**, **sample_mflix**, **test** - Other unrelated databases

---

## Database: `humanbenchmark`

### Collection: `gamesessions`

**Purpose:** Stores all game sessions including Märchenweber (storytelling game) sessions.

**Document Structure:**

```javascript
{
  _id: ObjectId("690794d8fa3239b8cf8fc28b"),
  userId: "690627f9ad18ee1e055dcb6f",  // String! Not ObjectId reference
  gameType: "maerchenweber",

  // Character info
  character_name: "Lara",
  character_description: "Eine Zahnfee...",
  story_theme: "In einer verzauberten stadt",
  reading_level: "second_grade",

  // Story data (OLD FORMAT - being phased out)
  history: [
    "Story text 1...",
    "[Wahl]: User choice 1",
    "Story text 2...",
    "[Wahl]: User choice 2",
    // ... alternating pattern
  ],

  // Story data (NEW FORMAT - current)
  turns: [
    {
      turn_number: 0,
      timestamp: ISODate("..."),
      user_choice: "User's choice text",
      story_text: "Story text...",
      choices: ["Option 1", "Option 2", "Option 3"],
      image_url: "https://...",
      scene_analysis: {...}
    },
    // ... more turns
  ],

  // Metadata
  generation_status: "ready",
  score: 0,
  round: 8,
  createdAt: ISODate("..."),
  lastUpdated: ISODate("..."),

  // Character tracking
  character_registry: [
    {
      name: "Lara",
      first_seen_round: 1,
      last_seen_round: 8,
      description: "..."
    }
  ],

  // Image generation
  pending_image: {...},
  image_history: [...]
}
```

**Key Facts:**
- `userId` is a **string**, not an ObjectId reference
- `userId` contains the ObjectId of a user from `myFirstDatabase.users`
- Old sessions use `history` array of strings
- New sessions use `turns` array of objects
- Both formats may coexist during migration period

---

## Database: `myFirstDatabase`

### Collection: `users`

**Purpose:** Stores user authentication data.

**Document Structure:**

```javascript
{
  _id: ObjectId("690627f9ad18ee1e055dcb6f"),
  name: "Lia2",  // Username
  createdAt: ISODate("...")
}
```

**Key Facts:**
- This is the **only** users collection for the application
- User ObjectId is stored as a **string** in `humanbenchmark.gamesessions.userId`
- Field name is `name`, not `username`

---

## Relationship: Users → Game Sessions

**User in myFirstDatabase:**
```javascript
{
  _id: ObjectId("690627f9ad18ee1e055dcb6f"),
  name: "Lia2"
}
```

**Game Session in humanbenchmark:**
```javascript
{
  _id: ObjectId("690794d8fa3239b8cf8fc28b"),
  userId: "690627f9ad18ee1e055dcb6f",  // String, not ObjectId!
  gameType: "maerchenweber",
  character_name: "Lara",
  // ...
}
```

**To find sessions for a user:**

1. Look up user in `myFirstDatabase.users` by `name` field
2. Get the user's `_id` as a string
3. Query `humanbenchmark.gamesessions` where `userId` equals that string

**Example:**
```javascript
// Step 1: Find user
const user = db.users.findOne({ name: "Lia2" });
// user._id = ObjectId("690627f9ad18ee1e055dcb6f")

// Step 2: Find sessions (userId is stored as STRING)
const sessions = db.gamesessions.find({
  userId: "690627f9ad18ee1e055dcb6f",  // String, not ObjectId!
  gameType: "maerchenweber"
});
```

---

## Frontend vs Backend Database Access

### SvelteKit (Frontend)
- Uses `MONGODB_URI` from `.env`
- Connects to `myFirstDatabase` for user management
- Code location: `src/lib/db/client.ts`
- Database name: Extracted from connection URI or defaults

### FastAPI (Backend - Märchenweber)
- Uses same `MONGODB_URI` from `.env`
- Explicitly uses `humanbenchmark` database
- Code location: `backend/app/database.py`
- Line: `_database = client["humanbenchmark"]`

**Key Fact:** Both services share the same MongoDB cluster but access different databases.

---

## History vs Turns Format

### Old Format (history)

Array of strings, alternating story text and user choices:

```javascript
history: [
  "Du bist Lara...",           // Story text
  "[Wahl]: Ich gehe links",    // User choice
  "Du gehst nach links...",    // Story text
  "[Wahl]: Ich öffne die Tür", // User choice
  // ...
]
```

### New Format (turns)

Array of structured objects:

```javascript
turns: [
  {
    turn_number: 0,
    timestamp: ISODate("..."),
    user_choice: "Ich gehe links",
    story_text: "Du bist Lara...",
    choices: ["Ich gehe links", "Ich gehe rechts", "Ich bleibe stehen"],
    image_url: "https://...",
    scene_analysis: {
      intensity: 3,
      perspective: "close",
      lighting: "warm"
    }
  },
  // ...
]
```

**Migration Status:**
- Old sessions may still have `history` format
- New sessions use `turns` format
- Migration script: `backend/migrate_story_tool.py`

---

## Common Queries

### Find user by username
```javascript
db.getSiblingDB('myFirstDatabase').users.findOne({ name: "Lia2" })
```

### Find all Märchenweber sessions for a user
```javascript
db.gamesessions.find({
  userId: "690627f9ad18ee1e055dcb6f",  // String!
  gameType: "maerchenweber"
})
```

### Check if session is migrated
```javascript
db.gamesessions.findOne(
  { _id: ObjectId("...") },
  { turns: 1, history: 1 }
)
// Has turns: migrated
// Only has history: needs migration
```

### Find sessions needing migration
```javascript
db.gamesessions.find({
  gameType: "maerchenweber",
  turns: { $exists: false }
})
```

---

## Important Notes

1. **userId is a STRING, not ObjectId reference**
   - MongoDB does not enforce foreign key relationships
   - The string value is the ObjectId from myFirstDatabase.users

2. **User collection is in a different database**
   - Users: `myFirstDatabase.users`
   - Sessions: `humanbenchmark.gamesessions`

3. **Multiple database names exist**
   - Not all databases are related to this project
   - `mongodb` database contains unrelated data

4. **No JOIN operations**
   - Must query users and sessions separately
   - Application code handles the relationship

5. **Migration is in progress**
   - Old format: `history` array
   - New format: `turns` array
   - Both may coexist temporarily

---

## Environment Configuration

**File:** `.env` (root directory)

```bash
MONGODB_URI=mongodb+srv://kids-games:password@cluster0.c6qg4eq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

**Used by:**
- SvelteKit: `src/lib/db/client.ts`
- FastAPI: `backend/app/database.py`

---

## Tools

### Migration Script
**File:** `backend/migrate_story_tool.py`

**Usage:**
```bash
cd backend
uv run python migrate_story_tool.py
```

**What it does:**
1. Searches for user by username
2. Finds their game sessions
3. Converts `history` (strings) to `turns` (objects)
4. Updates database while keeping original `history` as backup

---

## Schema Validation

**None.** MongoDB has no enforced schema. Document structure is defined by application code only.

---

## Indexes

**Collection:** `humanbenchmark.gamesessions`

```javascript
{
  userId: 1,
  gameType: 1,
  lastUpdated: -1
}
```

**Purpose:** Optimize queries for user session lists sorted by date.

**Created by:** `backend/app/database.py` on startup

---

## Summary

- **2 databases used:** `myFirstDatabase` (users), `humanbenchmark` (game data)
- **No foreign keys:** Relationship is string-based, not enforced
- **2 story formats:** `history` (old), `turns` (new)
- **1 migration tool:** `backend/migrate_story_tool.py`
- **Shared connection:** Both SvelteKit and FastAPI use same MongoDB URI
