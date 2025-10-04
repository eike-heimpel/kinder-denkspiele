---
title: "Tech Stack Reference"
purpose: "Detailed technical specifications for all technologies used"
audience: "AI agents, developers"
last_updated: "2025-10-03"
keywords: ["sveltekit", "svelte-5", "tailwind-v4", "mongodb", "typescript", "vite"]
related_docs: ["CLAUDE.md", "ARCHITECTURE.md", "TROUBLESHOOTING.md"]
---

# 🛠️ Tech Stack Reference

**Purpose:** Deep technical details for AI agents working with this codebase.  
**Related Docs:** [CLAUDE.md](./CLAUDE.md) | [ARCHITECTURE.md](./ARCHITECTURE.md) | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## Core Technologies

### SvelteKit 2.43.2
**Type:** Full-stack framework  
**Purpose:** Routing, SSR, API endpoints, build system

**Key Features Used:**
- File-based routing (`src/routes/`)
- Server routes (`+server.ts` files)
- Load functions (`+page.js`, `+page.server.js`)
- Form actions (not currently used, but available)
- Environment variables (`$env/static/private`)

**Gotchas:**
- `+server.ts` files handle API endpoints
- `+page.svelte` files are UI pages
- `+layout.svelte` wraps all pages
- Must connect to DB in each API endpoint (no global middleware)

**Config File:** `svelte.config.js`

---

### Svelte 5.39.5
**Type:** UI framework (compiler)  
**Purpose:** Component-based reactive UI

**CRITICAL:** This is Svelte 5, NOT Svelte 4. The syntax is completely different.

#### Svelte 5 Runes

**State Management:**
```typescript
// Reactive state
let count = $state(0);

// Derived/computed values
let doubled = $derived(count * 2);

// Side effects
$effect(() => {
    console.log('count changed:', count);
});

// Cleanup
$effect(() => {
    const interval = setInterval(() => {...}, 1000);
    return () => clearInterval(interval); // cleanup
});
```

**Component Communication:**
```typescript
// Props (receiving)
let { name, age = 18, optional } = $props();

// Children (rendering)
let { children } = $props();
{@render children()}

// Snippets (like slots, but better)
{#snippet header()}
    <h1>Title</h1>
{/snippet}

{@render header()}
```

**Event Handling:**
```svelte
<!-- Svelte 5 -->
<button onclick={handleClick}>Click</button>

<!-- NOT Svelte 4 syntax (DON'T use) -->
<button on:click={handleClick}>Click</button>
```

**Bindings:**
```svelte
<!-- Still the same -->
<input bind:value={text} />
```

**Conditional Rendering:**
```svelte
<!-- Same as Svelte 4 -->
{#if condition}
    <p>True</p>
{:else}
    <p>False</p>
{/if}
```

**Loops:**
```svelte
<!-- Same as Svelte 4 -->
{#each items as item}
    <p>{item.name}</p>
{/each}
```

**Migration from Svelte 4:**
- `export let prop` → `let { prop } = $props()`
- `<slot />` → `{@render children()}`
- `$:` reactive statements → `$derived()` or `$effect()`
- `on:event` → `onevent`

---

### Tailwind CSS 4.1.13
**Type:** Utility-first CSS framework  
**Purpose:** Styling without writing custom CSS

**CRITICAL:** This is Tailwind v4, NOT v3. The import syntax is different.

#### Tailwind v4 Configuration

**Import Syntax (REQUIRED):**
```css
/* src/app.css */
@import "tailwindcss";

/* NOT v3 syntax (DON'T use): */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Vite Plugin Setup:**
```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    plugins: [tailwindcss(), sveltekit()]
});
```

**No Config File Needed:**
- Tailwind v4 works without `tailwind.config.js`
- Classes are JIT compiled automatically
- Custom configuration can be added via CSS variables

**Key Classes Used:**
- Gradients: `bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400`
- Text gradients: `bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent`
- Glass-morphism: `bg-white/95 backdrop-blur-sm`
- Shadows: `shadow-lg`, `shadow-xl`, `shadow-2xl`
- Rounded corners: `rounded-xl`, `rounded-2xl`, `rounded-3xl`
- Spacing: `p-8`, `m-4`, `gap-6`

**Responsive Design:**
```html
<!-- Mobile first -->
<div class="p-4 md:p-8 lg:p-12">
```

**Hover/Active States:**
```html
<button class="hover:scale-105 active:scale-95 transition-all">
```

**Custom Animations:**
```svelte
<!-- In component <style> tag -->
<style>
    @keyframes customAnim {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .my-animation {
        animation: customAnim 1s ease-in-out;
    }
</style>
```

---

### MongoDB 6.20.0 (Node.js Driver)
**Type:** NoSQL database  
**Purpose:** Persistent data storage

**Connection Pattern:**
```typescript
// Singleton pattern - one connection for entire app
let client: MongoClient | null = null;
let db: Db | null = null;

export async function connectToDatabase(): Promise<Db> {
    if (db) return db; // Reuse existing connection
    
    client = new MongoClient(MONGODB_URI);
    await client.connect();
    db = client.db();
    return db;
}
```

**Collections:**
- `users` - User profiles
- `game_sessions` - Game session data

**Schemas:**
```typescript
// User
{
    _id: ObjectId,
    name: string,
    createdAt: Date
}

// GameSession
{
    _id: ObjectId,
    userId: string,
    gameType: 'verbal-memory',
    difficulty: 'easy' | 'hard',
    score: number,
    lives: number,
    wordsShown: string[],
    seenWords: string[],
    isActive: boolean,
    startedAt: Date,
    endedAt?: Date
}
```

**Common Operations:**
```typescript
// Insert
const result = await collection.insertOne(doc);

// Find one
const doc = await collection.findOne({ _id: new ObjectId(id) });

// Find many
const docs = await collection.find({ userId: 'xxx' }).toArray();

// Update
await collection.updateOne(
    { _id: new ObjectId(id) },
    { $set: { score: 10 } }
);

// Delete
await collection.deleteOne({ _id: new ObjectId(id) });
```

**ObjectId Handling:**
```typescript
import { ObjectId } from 'mongodb';

// String to ObjectId
const objectId = new ObjectId(stringId);

// ObjectId to String
const stringId = objectId.toString();
```

---

### TypeScript 5.9.2
**Type:** Type system for JavaScript  
**Purpose:** Type safety, better DX

**Configuration:** `tsconfig.json`

**Key Features Used:**
- Strict mode enabled
- Interface definitions
- Type exports
- Generic types
- Union types

**Type Files:**
- `src/lib/types/index.ts` - All app types
- `src/env.d.ts` - Environment variable types
- `src/app.d.ts` - SvelteKit app types
- `.svelte-kit/types/` - Generated types

**Common Patterns:**
```typescript
// Interfaces
export interface User {
    _id?: string;
    name: string;
    createdAt: Date;
}

// Union types
export type DifficultyLevel = 'easy' | 'hard';

// Generic types
async function findById<T>(id: string): Promise<T | null>

// Type guards
if (typeof value === 'string') { ... }

// Optional chaining
const score = session?.score ?? 0;
```

---

### Vite 7.1.7
**Type:** Build tool  
**Purpose:** Dev server, HMR, bundling

**Config File:** `vite.config.ts`

**Features:**
- Hot Module Replacement (HMR)
- Fast dev server
- Optimized production builds
- Plugin system

**Plugins Used:**
- `@tailwindcss/vite` - Tailwind CSS integration
- `@sveltejs/vite-plugin-svelte` - Svelte support (via SvelteKit)

**Commands:**
- `npm run dev` - Start dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

---

### Docker (MongoDB Container)
**Purpose:** Run MongoDB locally without installation

**File:** `docker-compose.yml`

**Configuration:**
```yaml
services:
  mongodb:
    image: mongo:8.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
```

**Commands:**
```bash
# Start MongoDB
docker-compose up -d

# Stop MongoDB
docker-compose down

# View logs
docker-compose logs mongodb

# Access MongoDB shell
docker exec -it kinder-denkspiele-mongo mongosh kinder-denkspiele

# View databases
show dbs

# View collections
show collections

# Query data
db.users.find()
db.game_sessions.find()
```

---

## Dependency Overview

### Production Dependencies
```json
{
    "mongodb": "^6.20.0"  // Only production dependency
}
```

### Development Dependencies
```json
{
    "@sveltejs/adapter-auto": "^6.1.0",
    "@sveltejs/kit": "^2.43.2",
    "@sveltejs/vite-plugin-svelte": "^6.2.0",
    "@tailwindcss/vite": "^4.1.13",
    "svelte": "^5.39.5",
    "svelte-check": "^4.3.2",
    "tailwindcss": "^4.1.13",
    "typescript": "^5.9.2",
    "vite": "^7.1.7"
}
```

---

## Version Constraints

### Node.js
- **Minimum:** Node 22.12.0 or Node 24.0.0
- **Recommended:** Node 24.9.0
- **Why:** @sveltejs/vite-plugin-svelte@6.2.1 requires this

**Check version:**
```bash
node --version
```

**Install correct version:**
```bash
nvm install 24
nvm use 24
nvm alias default 24
```

### npm
- **Minimum:** 10.0.0
- **Current:** 11.6.0

---

## Environment Variables

**File:** `.env` (gitignored)

**Required:**
```bash
MONGODB_URI=mongodb://localhost:27017/kinder-denkspiele
```

**Type Declaration:** `src/env.d.ts`
```typescript
declare module '$env/static/private' {
    export const MONGODB_URI: string;
}
```

**Usage:**
```typescript
import { MONGODB_URI } from '$env/static/private';
```

---

## Build Process

### Development
1. Vite starts dev server
2. SvelteKit handles routing
3. Svelte compiles components
4. Tailwind generates CSS
5. TypeScript type checks (separate process)

### Production
1. `npm run build`
2. SvelteKit builds app
3. Svelte compiles to optimized JS
4. Tailwind purges unused CSS
5. Vite bundles and minifies
6. Output in `.svelte-kit/output/`

---

## API Design

### Request Handler Type
```typescript
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params, url, request }) => {
    // params: route parameters
    // url: URL object
    // request: Request object
    
    return json(data);
};
```

### Response Helpers
```typescript
import { json, error } from '@sveltejs/kit';

// Success response
return json({ data: 'value' });

// Error response
return json({ error: 'Message' }, { status: 400 });

// Or throw error
error(404, 'Not found');
```

---

## File Naming Conventions

**SvelteKit Special Files:**
- `+page.svelte` - Page component
- `+page.ts` - Page data loader (runs on client and server)
- `+page.server.ts` - Server-only data loader
- `+layout.svelte` - Layout wrapper
- `+layout.ts` - Layout data loader
- `+server.ts` - API endpoint
- `+error.svelte` - Error page

**Regular Files:**
- `*.svelte` - Svelte component
- `*.ts` - TypeScript file
- `*.service.ts` - Service layer
- `*.repository.ts` - Repository layer

---

## Import Aliases

**Configured in:** `svelte.config.js` and `tsconfig.json`

```typescript
// $lib - alias for src/lib
import { Button } from '$lib/components/Button.svelte';

// $env - environment variables
import { MONGODB_URI } from '$env/static/private';

// $app - SvelteKit runtime
import { goto } from '$app/navigation';
import { page } from '$app/stores';
```

---

## Performance Considerations

### Svelte 5
- Fine-grained reactivity (only updates what changed)
- Smaller bundle size than Svelte 4
- Faster initial render

### Tailwind CSS
- JIT compilation (only generates used classes)
- Minimal CSS output
- No unused styles in production

### MongoDB
- Connection pooling via singleton
- Indexed queries (add indexes for production)
- Cursor-based pagination for large datasets

### Vite
- Fast HMR (<50ms)
- Code splitting
- Tree shaking
- Minification

---

## Browser Compatibility

**Targets:** Modern browsers only (ES2020+)
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Not Supported:**
- IE11 (obsolete)
- Older mobile browsers

---

## Development Tools

### Type Checking
```bash
npm run check  # Run svelte-check
```

### Formatting
- No formatter configured (uses editor defaults)
- Recommend: Prettier with Svelte plugin

### Linting
- No linter configured
- Recommend: ESLint with TypeScript + Svelte plugins

---

## Related Documentation

- **System Architecture:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Getting Started:** [QUICKSTART.md](./QUICKSTART.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **AI Guide:** [AI-GUIDE.md](./AI-GUIDE.md)
- **Theming:** [THEMING.md](./THEMING.md)
