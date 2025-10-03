---
title: "Routes Layer Documentation"
purpose: "SvelteKit routing structure - pages and API endpoints"
parent: "../../CLAUDE.md"
last_updated: "2025-10-03"
keywords: ["routes", "sveltekit", "pages", "api", "endpoints", "routing"]
---

# 🛣️ Routes Layer - Pages & API

**Layer:** Routing Layer  
**Location:** `src/routes/`  
**Parent Guide:** [Main CLAUDE.md](../../CLAUDE.md)

---

## 🎯 Purpose

The routes directory defines all pages and API endpoints using SvelteKit's file-based routing:
- **Pages:** `.svelte` files (UI components)
- **API Endpoints:** `+server.ts` files (backend logic)
- **Layouts:** `+layout.svelte` files (shared UI structure)

---

## 📂 Directory Structure

```
src/routes/
├── +layout.svelte          # Root layout (global CSS, nav)
├── +page.svelte            # Home page (user/game selection)
│
├── api/                    # API endpoints (backend)
│   ├── users/
│   │   ├── +server.ts      # GET, POST /api/users
│   │   └── [id]/
│   │       └── +server.ts  # GET, DELETE /api/users/:id
│   │
│   └── game/
│       ├── verbal-memory/
│       │   ├── start/+server.ts
│       │   ├── answer/+server.ts
│       │   └── stats/+server.ts
│       │
│       ├── visual-memory/
│       │   ├── start/+server.ts
│       │   ├── answer/+server.ts
│       │   └── stats/+server.ts
│       │
│       └── reaction-time/
│           ├── start/+server.ts
│           ├── submit/+server.ts
│           └── stats/+server.ts
│
├── game/                   # Game pages (frontend)
│   ├── verbal-memory/
│   │   └── +page.svelte
│   ├── visual-memory/
│   │   └── +page.svelte
│   └── reaction-time/
│       └── +page.svelte
│
└── stats/                  # Statistics pages
    └── [userId]/
        └── +page.svelte    # User stats page
```

---

## 🔗 Module-Specific Guides

For detailed documentation:

- **[api/CLAUDE.md](./api/CLAUDE.md)** - API endpoint implementation
- **[game/CLAUDE.md](./game/CLAUDE.md)** - Game page components

---

## 🏠 Root Layout

**File:** `+layout.svelte`

Global layout applied to all pages.

### Responsibilities

- Imports global CSS (`app.css` with Tailwind)
- Can include navigation (currently none)
- Defines common page structure
- Renders child pages via `<slot />`

### Content

```svelte
<script>
  import '../app.css';
</script>

<slot />
```

**Note:** Minimal layout. Pages handle their own structure.

---

## 🏡 Home Page

**File:** `+page.svelte`

Landing page with user selection and game selection.

### Features

- Create new user
- Select existing user
- Choose game type (Verbal Memory, Visual Memory, Reaction Time)
- Select difficulty (Easy/Hard)
- View user statistics
- Gradient background
- Kid-friendly UI

### URL

```
http://localhost:5173/
```

### Navigation

From home page:
- **Start Game:** `/game/[game-type]?userId=X&difficulty=Y`
- **View Stats:** `/stats/[userId]`

---

## 🎮 Game Pages

**Directory:** `game/`

Individual game pages for each game type.

**Files:**
- `verbal-memory/+page.svelte` - Word memory game
- `visual-memory/+page.svelte` - Grid memory game
- `reaction-time/+page.svelte` - Reaction speed test

**See:** [game/CLAUDE.md](./game/CLAUDE.md) for details

---

## 📊 Stats Page

**File:** `stats/[userId]/+page.svelte`

Displays historical statistics for all games for a specific user.

### URL

```
/stats/507f1f77bcf86cd799439011
```

### Features

- Shows stats for all three games
- Separate stats for easy/hard difficulty
- Historical data (total games, high score, average)
- Back to home button

### Data Loading

```typescript
// Fetches from multiple API endpoints
const verbalEasy = await fetch(`/api/game/verbal-memory/stats?userId=${userId}&difficulty=easy`);
const visualEasy = await fetch(`/api/game/visual-memory/stats?userId=${userId}&difficulty=easy`);
const reactionEasy = await fetch(`/api/game/reaction-time/stats?userId=${userId}&difficulty=easy`);
// ... repeat for hard difficulty
```

---

## 🔌 API Endpoints

**Directory:** `api/`

Backend endpoints for data operations.

**See:** [api/CLAUDE.md](./api/CLAUDE.md) for complete API documentation

---

## 🗺️ SvelteKit Routing

### File-Based Routing

| File | Route | Purpose |
|------|-------|---------|
| `+page.svelte` | `/` | Home page |
| `game/verbal-memory/+page.svelte` | `/game/verbal-memory` | Game page |
| `stats/[userId]/+page.svelte` | `/stats/123` | Dynamic route |
| `api/users/+server.ts` | `/api/users` | API endpoint |

### Dynamic Routes

Use `[param]` syntax:
```
stats/[userId]/+page.svelte  → /stats/507f1f77bcf86cd799439011
api/users/[id]/+server.ts    → /api/users/507f1f77bcf86cd799439011
```

Access params:
```typescript
// In +page.svelte
import { page } from '$app/stores';
const userId = $page.params.userId;

// In +server.ts
export const GET: RequestHandler = async ({ params }) => {
  const id = params.id;
  // ...
};
```

### Query Parameters

```typescript
// URL: /game/verbal-memory?userId=123&difficulty=easy

import { page } from '$app/stores';
const userId = $page.url.searchParams.get('userId');
const difficulty = $page.url.searchParams.get('difficulty');
```

---

## 🧭 Navigation

### Programmatic Navigation

```typescript
import { goto } from '$app/navigation';

function startGame() {
  goto(`/game/verbal-memory?userId=${userId}&difficulty=easy`);
}
```

### Link Navigation

```svelte
<a href="/game/verbal-memory?userId={userId}&difficulty=easy">
  Start Game
</a>
```

---

## 🔄 Common Patterns

### Page with Data Loading

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  let userId = $state('');
  let data = $state(null);
  
  onMount(async () => {
    userId = $page.params.userId;
    
    const response = await fetch(`/api/users/${userId}`);
    data = await response.json();
  });
</script>

{#if data}
  <div>{data.name}</div>
{:else}
  <div>Loading...</div>
{/if}
```

### API Endpoint with Error Handling

```typescript
import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.json();
    
    // Validate
    if (!body.name) {
      return json({ error: 'Name required' }, { status: 400 });
    }
    
    // Process
    const result = await doSomething(body);
    
    return json(result);
  } catch (error) {
    console.error(error);
    return json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
};
```

---

## 🆕 Adding New Routes

### Adding a Page

1. Create file: `src/routes/new-page/+page.svelte`

```svelte
<script lang="ts">
  let message = $state('Hello World');
</script>

<div class="min-h-screen flex items-center justify-center">
  <h1 class="text-4xl font-bold">{message}</h1>
</div>
```

2. Navigate to: `http://localhost:5173/new-page`

### Adding an API Endpoint

1. Create file: `src/routes/api/new-endpoint/+server.ts`

```typescript
import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  return json({ message: 'Hello from API' });
};

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();
  return json({ received: body });
};
```

2. Call from frontend:

```typescript
const response = await fetch('/api/new-endpoint');
const data = await response.json();
```

---

## 🐛 Common Issues

### Issue: 404 on page refresh
**Solution:** Ensure SvelteKit adapter is configured correctly

### Issue: API endpoint not found
**Solution:** Check file is named `+server.ts` (not `server.ts`)

### Issue: Dynamic route not matching
**Solution:** Verify bracket syntax `[param]` in folder name

**See:** [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../CLAUDE.md) - Entry point
- [api/CLAUDE.md](./api/CLAUDE.md) - API implementation
- [game/CLAUDE.md](./game/CLAUDE.md) - Game pages
- [ARCHITECTURE.md](../../ARCHITECTURE.md#routes) - Routing design
- [SvelteKit Routing Docs](https://kit.svelte.dev/docs/routing)

---

**SvelteKit's file-based routing makes adding new pages and endpoints straightforward and predictable.**

