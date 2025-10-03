---
title: "Quick Start Guide"
purpose: "Get the development environment running quickly"
audience: "AI agents, developers"
last_updated: "2025-10-03"
keywords: ["quickstart", "setup", "installation", "getting-started", "dev-environment"]
related_docs: ["CLAUDE.md", "TROUBLESHOOTING.md", "README.md"]
---

# 🚀 Quick Start Guide

## ✅ What's Already Done

Your Kinder Denkspiele app is **fully set up and running**!

- ✅ SvelteKit with Svelte 5 installed
- ✅ Tailwind CSS configured
- ✅ MongoDB running in Docker
- ✅ Development server running at `http://localhost:5173`

## 🎮 Test the App

1. **Open your browser**: http://localhost:5173

2. **Create a player**: 
   - Click "Neuer Spieler"
   - Enter a name (e.g., "Max" or "Emma")

3. **Play the game**:
   - Select your player
   - Choose "Verbales Gedächtnis"
   - Pick difficulty: 🟢 Einfach or 🔴 Schwer
   - Answer whether you've seen each word before

4. **Controls**:
   - Click buttons OR use keyboard
   - `←` or `N` = NEU (new word)
   - `→` or `G` = GESEHEN (seen before)

## 🛠️ Management Commands

### Start Everything
```bash
# Start MongoDB
docker-compose up -d

# Start dev server
npm run dev
```

### Stop Everything
```bash
# Stop dev server (Ctrl+C)

# Stop MongoDB
docker-compose down
```

### View MongoDB Data
```bash
docker exec -it kinder-denkspiele-mongo mongosh kinder-denkspiele

# In mongosh:
db.users.find()
db.game_sessions.find()
```

## 📦 Project Structure

```
src/
├── lib/
│   ├── types/              # All TypeScript types
│   ├── db/                 # MongoDB client
│   ├── repositories/       # Database operations (abstracted)
│   ├── services/           # Game logic (WordService, GameEngine)
│   ├── data/               # Word pools (easy: 70 words, hard: 75 words)
│   └── components/         # Reusable UI (Button, Card, GameStats)
│
└── routes/
    ├── +page.svelte        # Home/User selection
    ├── api/                # Server endpoints
    │   ├── users/          # User CRUD
    │   └── game/           # Game logic endpoints
    └── game/
        └── verbal-memory/  # Game UI
```

## 🎯 Key Features

### ✨ Well-Architected
- **Layered architecture**: Clear separation of concerns
- **Repository pattern**: Database logic abstracted
- **Service layer**: Game logic isolated and testable
- **Type-safe**: Full TypeScript coverage

### 🎨 Kid-Friendly
- Large, colorful buttons
- Simple German instructions
- Visual feedback (hearts for lives)
- Keyboard shortcuts for faster play

### 🔧 Extensible
- Easy to add new games (just follow the pattern)
- Word pools are separate and editable
- Stats system ready to expand
- API-first design

## 🚀 Adding New Games

1. **Add game type** in `src/lib/types/index.ts`:
   ```typescript
   export type GameType = 'verbal-memory' | 'reaction-time';
   ```

2. **Create service** in `src/lib/services/`:
   ```typescript
   export class ReactionTimeEngine { ... }
   ```

3. **Add API routes** in `src/routes/api/game/reaction-time/`

4. **Create UI** in `src/routes/game/reaction-time/+page.svelte`

5. **Add to home page** in `src/routes/+page.svelte`

## 📝 Customization

### Change Word Pools
Edit `src/lib/data/word-pools.ts`:
```typescript
export const germanWordPools: WordPool = {
  easy: ['Hund', 'Katze', ...],
  hard: ['Schmetterling', ...]
};
```

### Adjust Lives/Difficulty
Edit `src/lib/services/game-engine.service.ts`:
```typescript
lives: 3,  // Change this
```

### Modify UI Colors
Edit component files in `src/lib/components/` or page files in `src/routes/`

## 🐛 Troubleshooting

### MongoDB won't start
```bash
docker-compose down
docker-compose up -d
```

### Dev server won't start
```bash
# Kill any running process
killall node
npm run dev
```

### Type errors
```bash
npm run check
```

## 🎓 Next Steps

- Add more games (reaction time, number memory, etc.)
- Add sound effects
- Create a leaderboard
- Add animations
- Export/import user data
- Add achievements/badges

---

**Have fun playing!** 🎮🧠
