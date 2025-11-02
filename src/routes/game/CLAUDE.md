---
title: "Game Pages Documentation"
purpose: "Frontend game UI components and logic"
parent: "../../../CLAUDE.md"
last_updated: "2025-11-02"
keywords: ["game-pages", "ui", "svelte-5", "frontend", "gameplay", "interaction"]
---

# 🎮 Game Pages - Frontend UI

**Layer:** UI Layer (Game Pages)
**Location:** `src/routes/game/`
**Parent Guide:** [Main CLAUDE.md](../../../CLAUDE.md) | [Routes CLAUDE.md](../CLAUDE.md)

---

## 🎯 Purpose

Game pages handle the frontend gameplay experience:
- Display game UI
- Handle user interactions
- Call API endpoints
- Manage local game state
- Provide visual feedback

---

## 📂 Games (5 Total)

### Traditional Games
- **`verbal-memory/+page.svelte`** - Word memory game
- **`visual-memory/+page.svelte`** - Grid memory game
- **`reaction-time/+page.svelte`** - Reaction speed test

### LLM-Powered Games
- **`logic-lab/+page.svelte`** - Adaptive puzzle game (SvelteKit + LLM)
- **`maerchenweber/`** - Interactive storytelling (proxies to FastAPI backend)
  - `play/+page.svelte` - Active gameplay
  - `stories/+page.svelte` - Story library
  - `replay/[sessionId]/+page.svelte` - Replay saved stories

---

## 🗣️ Verbal Memory Game

**File:** `verbal-memory/+page.svelte`

**URL:** `/game/verbal-memory?userId=X&difficulty=Y`

### Features

- Display German words one at a time
- Two buttons: NEU (new) and GESEHEN (seen)
- Keyboard support: ← or N for NEU, → or G for GESEHEN
- Score and lives display
- Game over screen with replay option
- Smooth word transitions

### State Management

```typescript
let sessionId = $state('');
let currentWord = $state('');
let score = $state(0);
let lives = $state(3);
let gameOver = $state(false);
let message = $state('');
let userId = $state('');
let difficulty = $state<DifficultyLevel>('easy');
```

### Key Functions

```typescript
// Start game on mount
onMount(async () => {
  userId = $page.url.searchParams.get('userId') || '';
  difficulty = $page.url.searchParams.get('difficulty') as DifficultyLevel;
  
  const response = await fetch('/api/game/verbal-memory/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, difficulty })
  });
  
  const data = await response.json();
  sessionId = data.sessionId;
  currentWord = data.currentWord;
  score = data.score;
  lives = data.lives;
});

// Submit answer
async function submitAnswer(answer: 'seen' | 'new') {
  const response = await fetch('/api/game/verbal-memory/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, answer })
  });
  
  const data = await response.json();
  
  if (data.gameOver) {
    gameOver = true;
    message = data.message;
  } else {
    currentWord = data.currentWord;
    score = data.score;
    lives = data.lives;
  }
}

// Keyboard handler
function handleKeydown(e: KeyboardEvent) {
  if (gameOver) return;
  
  if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'n') {
    submitAnswer('new');
  } else if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'g') {
    submitAnswer('seen');
  }
}
```

### UI Structure

```svelte
<div class="min-h-screen gradient-background">
  <div class="container">
    <GameStats {score} {lives} />
    
    {#if !gameOver}
      <Card>
        <h2 class="text-6xl font-bold">{currentWord}</h2>
      </Card>
      
      <div class="button-group">
        <Button variant="primary" onclick={() => submitAnswer('new')}>
          ⬅️ NEU
        </Button>
        <Button variant="secondary" onclick={() => submitAnswer('seen')}>
          GESEHEN ➡️
        </Button>
      </div>
    {:else}
      <!-- Game over screen -->
      <Card>
        <h2>{message}</h2>
        <Button onclick={replayGame}>🔄 Nochmal spielen</Button>
      </Card>
    {/if}
  </div>
</div>
```

---

## 🎯 Visual Memory Game

**File:** `visual-memory/+page.svelte`

**URL:** `/game/visual-memory?userId=X&difficulty=Y`

### Features

- Display grid (3x3 or 4x4)
- Highlight target squares (blue)
- Three phases:
  1. **Presentation:** Show targets (2s or 1.5s)
  2. **Retention:** Blank grid with delay (1s or 1.5s)
  3. **Recall:** User selects squares
- Feedback after each round
- Progressive difficulty (more targets every 2 rounds)

### Game Phases

```typescript
type GamePhase = 'presentation' | 'retention' | 'recall' | 'feedback';
let phase = $state<GamePhase>('presentation');
```

### State Management

```typescript
let sessionId = $state('');
let score = $state(0);
let lives = $state(3);
let round = $state(1);
let gameOver = $state(false);

// Visual memory specific
let gridSize = $state(3);
let targetPositions = $state<number[]>([]);
let userSelections = $state<number[]>([]);
let previousTargets = $state<number[]>([]);
```

### Phase Flow

```typescript
async function startRound() {
  // 1. Presentation phase
  phase = 'presentation';
  userSelections = [];
  
  await sleep(presentationTime);
  
  // 2. Retention phase
  phase = 'retention';
  
  await sleep(retentionDelay);
  
  // 3. Recall phase
  phase = 'recall';
  // User interacts...
}

function handleCellClick(index: number) {
  if (phase !== 'recall') return;
  
  if (userSelections.includes(index)) {
    userSelections = userSelections.filter(i => i !== index);
  } else {
    userSelections = [...userSelections, index];
  }
}

async function submitAnswer() {
  const response = await fetch('/api/game/visual-memory/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, userSelections })
  });
  
  const data = await response.json();
  
  // Show feedback
  phase = 'feedback';
  previousTargets = data.previousTargets;  // CRITICAL for feedback
  
  await sleep(2000);
  
  if (data.gameOver) {
    gameOver = true;
  } else {
    // Next round
    targetPositions = data.visualMemoryState.targetPositions;
    score = data.score;
    lives = data.lives;
    round = data.round;
    startRound();
  }
}
```

### UI with VisualMemoryGrid Component

```svelte
{#if phase === 'presentation'}
  <VisualMemoryGrid
    {gridSize}
    targetPositions={targetPositions}
    showTargets={true}
    disabled={true}
  />
{:else if phase === 'recall'}
  <VisualMemoryGrid
    {gridSize}
    targetPositions={[]}
    userSelections={userSelections}
    onCellClick={handleCellClick}
    showTargets={false}
  />
  <Button onclick={submitAnswer}>Bestätigen</Button>
{:else if phase === 'feedback'}
  <VisualMemoryGrid
    {gridSize}
    targetPositions={previousTargets}
    userSelections={userSelections}
    showFeedback={true}
    showTargets={true}
    disabled={true}
  />
{/if}
```

**Important:** Use `previousTargets` for feedback, not `targetPositions` (which contains next round's targets).

---

## ⚡ Reaction Time Game

**File:** `reaction-time/+page.svelte`

**URL:** `/game/reaction-time?userId=X&difficulty=Y`

### Features

- Red screen initially ("Warte...")
- Random delay (2-4s easy, 1-3s hard)
- Green screen ("JETZT! Klicke!")
- Record reaction time in milliseconds
- Penalize false starts (clicking too early)
- 5 rounds total
- Show average reaction time at end

### Game States

```typescript
type GameState = 'waiting' | 'ready' | 'clicked' | 'false-start';
let gameState = $state<GameState>('waiting');
```

### State Management

```typescript
let sessionId = $state('');
let round = $state(1);
let reactionTimes = $state<number[]>([]);
let falseStarts = $state(0);
let gameOver = $state(false);
let averageTime = $state(0);

// Timing
let startTime = $state(0);
let timeoutId: number | null = null;
```

### Round Flow

```typescript
async function startRound() {
  gameState = 'waiting';
  
  // Random delay
  const delay = minDelay + Math.random() * (maxDelay - minDelay);
  
  timeoutId = setTimeout(() => {
    gameState = 'ready';
    startTime = Date.now();
  }, delay);
}

function handleClick() {
  if (gameState === 'waiting') {
    // False start!
    clearTimeout(timeoutId!);
    gameState = 'false-start';
    falseStarts++;
    
    setTimeout(() => {
      startRound();  // Try again
    }, 1000);
  } else if (gameState === 'ready') {
    // Good reaction!
    const reactionTime = Date.now() - startTime;
    gameState = 'clicked';
    
    submitReaction(reactionTime);
  }
}

async function submitReaction(reactionTime: number) {
  const response = await fetch('/api/game/reaction-time/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, reactionTime, isFalseStart: false })
  });
  
  const data = await response.json();
  
  if (data.gameOver) {
    gameOver = true;
    averageTime = data.score;
    reactionTimes = data.reactionTimeState.reactionTimes;
  } else {
    reactionTimes = data.reactionTimeState.reactionTimes;
    round = data.reactionTimeState.currentRound;
    
    setTimeout(() => {
      startRound();
    }, 1000);
  }
}
```

### UI with Color Feedback

```svelte
<div 
  class="min-h-screen flex items-center justify-center cursor-pointer"
  class:bg-red-500={gameState === 'waiting' || gameState === 'false-start'}
  class:bg-green-500={gameState === 'ready'}
  class:bg-blue-500={gameState === 'clicked'}
  onclick={handleClick}
>
  {#if gameState === 'waiting'}
    <h1 class="text-4xl">Warte auf Grün...</h1>
  {:else if gameState === 'ready'}
    <h1 class="text-6xl">JETZT! KLICKE!</h1>
  {:else if gameState === 'false-start'}
    <h1 class="text-4xl">❌ Zu früh!</h1>
  {:else if gameState === 'clicked'}
    <h1 class="text-4xl">✅ {reactionTimes[reactionTimes.length - 1]}ms</h1>
  {/if}
</div>
```

---

## 🧩 Logic Lab Game

**File:** `logic-lab/+page.svelte`

**URL:** `/game/logic-lab?userId=X`

### Features

- LLM-generated adaptive puzzles
- Age-based difficulty (4-10 years)
- 4 problem types: pattern, category, comparison, grouping
- Infinite mode (no question limit)
- Optional parent guidance
- Multiple choice answers (4 options)

### Game Phases

```typescript
type GamePhase = 'setup' | 'playing' | 'feedback' | 'gameOver';
let gamePhase = $state<GamePhase>('setup');
```

### Key State

```typescript
let sessionId = $state('');
let age = $state(7);
let guidance = $state('');
let currentProblem = $state<Problem | null>(null);
let score = $state(0);
let selectedAnswerIndex = $state(-1);
let lastAnswerCorrect = $state(false);
let explanation = $state('');
```

### Flow

1. **Setup:** User enters age and optional guidance
2. **Start:** Call `/api/game/logic-lab/start` with age and guidance
3. **Playing:** Display question with 4 options
4. **Submit:** Call `/api/game/logic-lab/answer` with answer index
5. **Feedback:** Show ✅ or ❌ with explanation (3 seconds)
6. **Next:** Load next problem, repeat

**Complete Documentation:** [docs/LOGIC-LAB.md](../../../docs/LOGIC-LAB.md)

---

## 🎭 Märchenweber Game

**Directory:** `maerchenweber/`

**Note:** This game proxies to a separate FastAPI backend running on port 8000.

### Sub-Pages

**Hub (`+page.svelte`):**
- Entry point
- Character creation
- Navigation to play/stories

**Play (`play/+page.svelte`):**
- Active storytelling session
- Story text display
- Image generation
- 3 choice buttons
- Journey recap (previous choices)
- Fun nuggets (during LLM wait time)
- Progress steps indicator

**Stories (`stories/+page.svelte`):**
- List of all user's past stories
- Click to replay

**Replay (`replay/[sessionId]/+page.svelte`):**
- Replay a saved story from start to finish
- Read-only (no new choices)

### Features

- LLM-powered dynamic storytelling (Gemini 2.5 Pro)
- AI image generation for each turn
- Character consistency across images
- Scene-adaptive image variation
- Safety validation
- Turn-based choice system
- Story persistence in MongoDB

**Complete Documentation:** [backend/CLAUDE.md](../../../../backend/CLAUDE.md)

---

## 🔄 Common Patterns Across Games

### URL Parameters

```typescript
import { page } from '$app/stores';

onMount(() => {
  const userId = $page.url.searchParams.get('userId');
  const difficulty = $page.url.searchParams.get('difficulty') as DifficultyLevel;
  
  if (!userId || !difficulty) {
    goto('/');  // Redirect if missing params
    return;
  }
  
  // Start game...
});
```

### API Calls

```typescript
async function callAPI(endpoint: string, body?: any) {
  try {
    const response = await fetch(endpoint, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined
    });
    
    if (!response.ok) {
      throw new Error('API call failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error(error);
    // Handle error...
  }
}
```

### Navigation

```typescript
import { goto } from '$app/navigation';

function returnHome() {
  goto('/');
}

function viewStats() {
  goto(`/stats/${userId}`);
}

function replayGame() {
  goto(`/game/verbal-memory?userId=${userId}&difficulty=${difficulty}`);
}
```

---

## 🆕 Adding a New Game Page

### Step-by-Step

1. **Create file** (`src/routes/game/new-game/+page.svelte`)

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import GameStats from '$lib/components/GameStats.svelte';
  import type { DifficultyLevel } from '$lib/types';
  
  // State
  let sessionId = $state('');
  let score = $state(0);
  let lives = $state(3);
  let gameOver = $state(false);
  let userId = $state('');
  let difficulty = $state<DifficultyLevel>('easy');
  
  // Start game
  onMount(async () => {
    userId = $page.url.searchParams.get('userId') || '';
    difficulty = $page.url.searchParams.get('difficulty') as DifficultyLevel;
    
    if (!userId || !difficulty) {
      goto('/');
      return;
    }
    
    const response = await fetch('/api/game/new-game/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, difficulty })
    });
    
    const data = await response.json();
    sessionId = data.sessionId;
    score = data.score;
    lives = data.lives;
  });
  
  // Game logic functions...
</script>

<div class="min-h-screen bg-gradient-to-br from-purple-400 to-blue-500">
  <div class="container mx-auto p-8">
    <GameStats {score} {lives} />
    
    {#if !gameOver}
      <Card>
        <!-- Game UI -->
      </Card>
    {:else}
      <Card>
        <h2 class="text-3xl">Game Over!</h2>
        <Button onclick={() => goto('/')}>Zurück</Button>
      </Card>
    {/if}
  </div>
</div>
```

2. **Create API endpoints** (see [api/CLAUDE.md](../api/CLAUDE.md))

3. **Add to home page** (`src/routes/+page.svelte`)

```svelte
<Button onclick={() => startGame('new-game', 'easy')}>
  🎮 New Game (Easy)
</Button>
```

---

## 🎨 Styling

All game pages use:
- Full-screen gradient backgrounds
- Tailwind utility classes
- Shared components (Button, Card, GameStats)
- Kid-friendly colors and fonts

```svelte
<div class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400">
  <div class="container mx-auto p-8">
    <!-- Content -->
  </div>
</div>
```

---

## 🐛 Common Issues

### Issue: Page loads but game doesn't start
**Solution:** Check userId and difficulty are in URL params

### Issue: Keyboard not working
**Solution:** Ensure `<svelte:window onkeydown={handleKeydown} />` is present

### Issue: State not updating
**Solution:** Use `$state()` syntax, not plain `let`

**See:** [TROUBLESHOOTING.md](../../../TROUBLESHOOTING.md)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../../CLAUDE.md) - Entry point
- [Routes CLAUDE.md](../CLAUDE.md) - Routing overview
- [api/CLAUDE.md](../api/CLAUDE.md) - Backend endpoints
- [components/CLAUDE.md](../../lib/components/CLAUDE.md) - UI components
- [services/CLAUDE.md](../../lib/services/CLAUDE.md) - Game logic

---

**Game pages are the player-facing interface. Focus on smooth interactions, clear feedback, and kid-friendly design.**

