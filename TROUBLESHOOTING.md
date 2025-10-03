---
title: "Troubleshooting Guide"
purpose: "Solutions to common development issues and errors"
audience: "AI agents, developers"
last_updated: "2025-10-03"
keywords: ["troubleshooting", "debugging", "errors", "issues", "fixes", "problems"]
related_docs: ["CLAUDE.md", "TECH-STACK.md", "QUICKSTART.md"]
---

# 🔧 Troubleshooting Guide

**Purpose:** Solutions to common issues encountered while developing this project.  
**Related Docs:** [CLAUDE.md](./CLAUDE.md) | [TECH-STACK.md](./TECH-STACK.md)

---

## 🚨 Critical Issues

### Tailwind CSS Not Working

**Symptoms:**
- Classes in HTML but no styling applied
- Looks like plain HTML (Times New Roman font, no colors)
- Test page with `bg-red-500` shows no red background

**Root Cause:**
Using Tailwind v3 syntax in a v4 project

**Solution:**
Update `src/app.css`:
```css
/* ✅ Correct (Tailwind v4) */
@import "tailwindcss";

/* ❌ Wrong (Tailwind v3 - don't use) */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Verification:**
```bash
# Check if CSS is being generated
curl -s http://localhost:5173 | grep "tailwindcss"
# Should see: /*! tailwindcss v4.1.14 | MIT License */
```

**Related:** [TECH-STACK.md](./TECH-STACK.md#tailwind-v4)

---

### MongoDB Connection Failed

**Symptoms:**
- Error: "MONGODB_URI environment variable is not set"
- Error: "MongoNetworkError: connect ECONNREFUSED"
- API endpoints fail with 500 error

**Solutions:**

**1. Missing Environment Variable**
Create `.env` file in project root:
```bash
echo "MONGODB_URI=mongodb://localhost:27017/kinder-denkspiele" > .env
```

**2. Missing Type Declaration**
Ensure `src/env.d.ts` exists:
```typescript
declare module '$env/static/private' {
    export const MONGODB_URI: string;
}
```

**3. MongoDB Not Running**
```bash
# Start MongoDB
docker-compose up -d

# Verify it's running
docker ps | grep mongo
```

**4. Wrong Connection String**
Check `.env` file has correct format:
```
MONGODB_URI=mongodb://localhost:27017/kinder-denkspiele
```

---

### Svelte 5 Syntax Errors

**Symptoms:**
- Error: "Unexpected token $state"
- Error: "slot is not defined"
- Components not rendering

**Common Issues:**

**1. Using Svelte 4 Syntax**
```svelte
<!-- ❌ Svelte 4 (don't use) -->
<script>
    export let name;
</script>
<slot />

<!-- ✅ Svelte 5 (correct) -->
<script>
    let { name } = $props();
    let { children } = $props();
</script>
{@render children()}
```

**2. Event Handler Syntax**
```svelte
<!-- ❌ Svelte 4 -->
<button on:click={handleClick}>

<!-- ✅ Svelte 5 -->
<button onclick={handleClick}>
```

**3. Reactive Statements**
```svelte
<script>
    // ❌ Svelte 4
    $: doubled = count * 2;
    
    // ✅ Svelte 5
    let doubled = $derived(count * 2);
</script>
```

**Related:** [TECH-STACK.md](./TECH-STACK.md#svelte-5-runes)

---

### Node Version Issues

**Symptoms:**
- Error: "engine Unsupported engine"
- Error: "Not compatible with your version of node/npm"
- npm install fails

**Root Cause:**
Need Node 24+ or Node 22.12+

**Solution:**
```bash
# Install Node 24
nvm install 24

# Use Node 24
nvm use 24

# Set as default
nvm alias default 24

# Verify
node --version  # Should show v24.x.x
```

**If nvm not installed:**
```bash
# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Windows
# Download nvm-windows from GitHub
```

---

## 🐛 Common Development Issues

### Hot Reload Not Working

**Symptoms:**
- Changes not reflected in browser
- Need to manually refresh
- Dev server seems frozen

**Solutions:**

**1. Hard Refresh Browser**
- Mac: `Cmd + Shift + R`
- Windows: `Ctrl + Shift + F5`

**2. Clear SvelteKit Cache**
```bash
rm -rf .svelte-kit
npm run dev
```

**3. Restart Dev Server**
```bash
# Kill the process
pkill -f "vite dev"

# Start again
npm run dev
```

**4. Check File Watching**
```bash
# On macOS, increase file watch limit
sudo sysctl -w kern.maxfiles=65536
sudo sysctl -w kern.maxfilesperproc=65536
```

---

### TypeScript Errors

**Symptoms:**
- Red squiggly lines in editor
- "Cannot find module" errors
- Type errors in terminal

**Solutions:**

**1. Run Type Check**
```bash
npm run check
```

**2. Restart TypeScript Server**
In VS Code: `Cmd/Ctrl + Shift + P` → "TypeScript: Restart TS Server"

**3. Check tsconfig.json**
Ensure it extends SvelteKit config:
```json
{
  "extends": "./.svelte-kit/tsconfig.json"
}
```

**4. Missing Type Definitions**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

### MongoDB ObjectId Issues

**Symptoms:**
- Error: "Argument passed in must be a string of 12 bytes"
- Error: "Cast to ObjectId failed"
- Database queries return null unexpectedly

**Solutions:**

**1. String to ObjectId Conversion**
```typescript
import { ObjectId } from 'mongodb';

// Always wrap in try-catch
try {
    const objectId = new ObjectId(stringId);
} catch (error) {
    // Invalid ObjectId format
    return json({ error: 'Invalid ID' }, { status: 400 });
}
```

**2. ObjectId to String**
```typescript
// When returning to client
return {
    _id: doc._id?.toString(),
    ...doc
};
```

**3. Null Check**
```typescript
const doc = await collection.findOne({ _id: new ObjectId(id) });

if (!doc) {
    return json({ error: 'Not found' }, { status: 404 });
}
```

---

### Import Path Issues

**Symptoms:**
- Error: "Cannot find module '$lib/...'"
- Error: "Cannot find module '$env/...'"
- Imports not resolving

**Solutions:**

**1. Check Import Alias**
```typescript
// ✅ Correct
import { Button } from '$lib/components/Button.svelte';

// ❌ Wrong
import { Button } from '../lib/components/Button.svelte';
```

**2. Restart Dev Server**
Changes to `svelte.config.js` require restart

**3. Check File Extension**
```typescript
// ✅ Include .svelte extension
import Button from '$lib/components/Button.svelte';

// ❌ Missing extension
import Button from '$lib/components/Button';
```

---

### CSS Not Loading

**Symptoms:**
- Styles not applied
- app.css changes not reflecting
- Missing Tailwind utilities

**Solutions:**

**1. Check Import in Layout**
```svelte
<!-- src/routes/+layout.svelte -->
<script>
    import "../app.css";  // Must be relative path
</script>
```

**2. Verify CSS Import Syntax**
```css
/* src/app.css */
@import "tailwindcss";  /* v4 syntax */
```

**3. Clear Browser Cache**
Hard refresh or clear cache

**4. Check Vite Config**
```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    plugins: [tailwindcss(), sveltekit()]
});
```

---

### Port Already in Use

**Symptoms:**
- Error: "Port 5173 is in use"
- Dev server won't start

**Solutions:**

**1. Kill Process on Port**
```bash
# macOS/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**2. Use Different Port**
```bash
npm run dev -- --port 3000
```

**3. Check for Zombie Processes**
```bash
ps aux | grep vite
kill -9 <PID>
```

---

### Database Queries Not Working

**Symptoms:**
- Query returns empty array
- findOne returns null
- Data not persisting

**Solutions:**

**1. Check Database Connection**
```typescript
// At start of API handler
await connectToDatabase();
```

**2. Verify Collection Name**
```typescript
const collection = db.collection('users');  // exact name
```

**3. Check Query Syntax**
```typescript
// ✅ Correct
const doc = await collection.findOne({ _id: new ObjectId(id) });

// ❌ Wrong (passing string directly)
const doc = await collection.findOne({ _id: id });
```

**4. Inspect MongoDB Data**
```bash
docker exec -it kinder-denkspiele-mongo mongosh kinder-denkspiele
db.users.find().pretty()
db.game_sessions.find().pretty()
```

---

## 🔍 Debugging Techniques

### Console Logging

**Server-side (API endpoints):**
```typescript
console.log('Received request:', { userId, difficulty });
// Appears in terminal where `npm run dev` is running
```

**Client-side (components):**
```typescript
console.log('Current state:', score, lives);
// Appears in browser DevTools console
```

**Effect Debugging:**
```typescript
$effect(() => {
    console.log('Score changed:', score);
});
```

---

### Browser DevTools

**Open DevTools:**
- Mac: `Cmd + Option + I`
- Windows: `F12`

**Useful Tabs:**
- **Console:** See errors and logs
- **Network:** See API requests/responses
- **Elements:** Inspect HTML and CSS
- **Sources:** Set breakpoints in code

**Common Checks:**
1. Check Network tab for failed API calls
2. Check Console for JavaScript errors
3. Inspect Elements to see if Tailwind classes are present
4. Check Application → Local Storage for any stored data

---

### MongoDB Shell Debugging

**Connect:**
```bash
docker exec -it kinder-denkspiele-mongo mongosh kinder-denkspiele
```

**Useful Commands:**
```javascript
// List databases
show dbs

// Use database
use kinder-denkspiele

// List collections
show collections

// Find all users
db.users.find().pretty()

// Find specific user
db.users.findOne({ name: "TestUser" })

// Count documents
db.users.countDocuments()

// Find recent sessions
db.game_sessions.find().sort({ startedAt: -1 }).limit(5).pretty()

// Delete test data
db.users.deleteMany({ name: /Test/ })
```

---

### Git History Debugging

**When was this file last changed?**
```bash
git log --oneline -- path/to/file
```

**What changed in this commit?**
```bash
git show <commit-hash>
```

**Who changed this line?**
```bash
git blame path/to/file
```

**Find when a bug was introduced:**
```bash
git bisect start
git bisect bad  # current version has bug
git bisect good <commit>  # this commit didn't have bug
# Git will guide you through binary search
```

---

## ⚠️ Known Issues

### Issue: Tailwind Purge in Production
**Status:** Not configured  
**Impact:** Larger CSS bundle in production  
**Solution:** Add content paths to Tailwind config (future enhancement)

### Issue: No User Authentication
**Status:** By design (local-only deployment)  
**Impact:** Anyone can access any user's data  
**Solution:** Add auth system for production deployment

### Issue: No Error Boundaries
**Status:** Not implemented  
**Impact:** Errors may crash entire app  
**Solution:** Add Svelte error boundaries (future enhancement)

### Issue: No Loading States
**Status:** Basic loading implemented  
**Impact:** Some operations may seem unresponsive  
**Solution:** Add skeleton loaders and better feedback

---

## 📞 Getting Help

### 1. Check Documentation
- [AI-GUIDE.md](./AI-GUIDE.md) - Start here
- [TECH-STACK.md](./TECH-STACK.md) - Tech details
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design

### 2. Search Codebase
```bash
# Find similar code
grep -r "pattern" src/

# Find function usage
grep -r "functionName" src/
```

### 3. Check External Docs
- [Svelte 5 Docs](https://svelte.dev/docs/svelte/overview)
- [SvelteKit Docs](https://svelte.dev/docs/kit/introduction)
- [Tailwind v4 Docs](https://tailwindcss.com/docs)
- [MongoDB Docs](https://www.mongodb.com/docs/drivers/node/current/)

### 4. Check Git History
```bash
# Recent changes
git log --oneline -10

# Changes to specific file
git log -- path/to/file
```

### 5. Isolate the Problem
- Create minimal reproduction in `/test` route
- Comment out code to find culprit
- Check one layer at a time (UI → API → Service → DB)

---

## 🛡️ Prevention

### Before Committing
```bash
# 1. Run tests
npm test -- --run

# 2. Type check
npm run check

# 3. Test in browser
# - Create user
# - Start game
# - Play through game
# - Check console for errors

# 4. Review changes
git diff

# 5. Descriptive commit message
git commit -m "What changed and why"
```

### Code Review Checklist
- [ ] Tests pass (`npm test -- --run`)
- [ ] Types defined for complex objects
- [ ] Error handling in API endpoints
- [ ] Input validation
- [ ] Console.logs removed (or commented)
- [ ] No hardcoded values
- [ ] Comments explain "why", not "what"
- [ ] Critical logic has unit tests

---

**Still Stuck?** Check [DECISIONS.md](./DECISIONS.md) to understand why things are built the way they are.
