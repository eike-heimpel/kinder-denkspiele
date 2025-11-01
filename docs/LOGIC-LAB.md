# Logic Lab Game - Developer Guide

**Game Type:** `logic-lab`
**Last Updated:** 2025-11-01
**Status:** Production Ready
**Model:** Google Gemini 2.5 Flash via OpenRouter

---

## 🎯 Overview

Logic Lab is an **LLM-powered adaptive problem-solving game** that generates unique problems dynamically based on the child's performance. Unlike the other games which use fixed word pools or pre-determined patterns, Logic Lab creates fresh content for every question.

### Key Features

- **Dynamic Generation:** Every problem is created by an LLM in real-time
- **Performance-Based Adaptation:** LLM adjusts difficulty by analyzing answer history
- **Initial Guidance:** Adults can provide context (age, interests, challenges)
- **4 Problem Types:** Riddles, patterns, categorization, cause-effect
- **15 Questions:** Long enough for meaningful adaptation
- **High Creativity:** Temperature 1.2 for diverse, interesting problems

---

## 🏗️ Architecture

### Layer Overview

```
UI Layer (Svelte 5)
  └─ /routes/game/logic-lab/+page.svelte
         ↓
API Layer (SvelteKit Routes)
  ├─ /routes/api/game/logic-lab/start/+server.ts
  ├─ /routes/api/game/logic-lab/answer/+server.ts
  └─ /routes/api/game/logic-lab/stats/+server.ts
         ↓
Service Layer
  ├─ LogicLabEngine (game logic, scoring, state)
  ├─ LLMService (OpenRouter API integration)
  └─ PromptLoader (YAML template rendering)
         ↓
Prompt Templates
  └─ /lib/prompts/generate-problem.yaml
         ↓
External API
  └─ OpenRouter → Google Gemini 2.5 Flash
```

---

## 📝 Prompt Template System

### YAML + Jinja2 Architecture

Logic Lab uses a sophisticated prompt template system that separates prompts from code:

**File:** `src/lib/prompts/generate-problem.yaml`

```yaml
version: "1.0.0"
model: "google/gemini-2.5-flash"
temperature: 1.2
max_tokens: 1000

system_prompt: |
  Du bist ein kreativer und geduldiger Lehrer für Kinder.
  # ... detailed instructions

user_prompt: |
  Erstelle ein neues kreatives {{ problem_type }}.

  {% if performance_history|length > 0 %}
  BISHERIGE PERFORMANCE:
  {% for item in performance_history %}
  - "{{ item.question }}" → {{ "✓" if item.correct else "✗" }}
  {% endfor %}
  {% endif %}
```

### Template Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `initial_guidance` | string | Adult-provided context |
| `age` | number | Child's age (5-8) |
| `difficulty` | string | Base difficulty (easy/hard) |
| `problem_type` | string | riddle/pattern/category/cause-effect |
| `performance_history` | array | Last 5 problems with results |
| `consecutive_correct` | number | Current success streak |
| `consecutive_incorrect` | number | Current failure streak |

### Why YAML + Jinja2?

1. **Separation of Concerns:** Prompts are content, not code
2. **Easy Iteration:** Modify prompts without touching TypeScript
3. **Version Control:** Track prompt changes independently
4. **Reusability:** Same template system for future LLM features
5. **Dynamic Content:** Jinja2 loops/conditionals for complex logic

### PromptLoader Service

**File:** `src/lib/services/prompt-loader.service.ts`

```typescript
export class PromptLoader {
  loadPrompt(name: string): PromptConfig;
  renderPrompt(name: string, variables: Record<string, any>): RenderedPrompt;
}
```

Handles:
- Loading YAML files from disk
- Parsing YAML structure
- Rendering Jinja2 templates with variables
- Validating required variables
- Returning structured prompt + model config

---

## 🧠 LLM Integration

### LLMService

**File:** `src/lib/services/llm.service.ts`

**Responsibilities:**
- OpenRouter API communication
- Prompt rendering via PromptLoader
- Response parsing and validation
- Content safety filtering
- Fallback problem generation

**Key Methods:**

```typescript
class LLMService {
  async generateProblem(params: GenerateProblemParams): Promise<Problem>
  private async callOpenRouter(rendered: RenderedPrompt): Promise<string>
  private parseResponse(content: string): Problem
  private validateProblem(problem: Problem): boolean
  private getFallbackProblem(difficulty: number): Problem
}
```

### OpenRouter Configuration

**API Endpoint:** `https://openrouter.ai/api/v1/chat/completions`

**Headers:**
```typescript
{
  'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
  'Content-Type': 'application/json',
  'HTTP-Referer': 'https://localhost:5173',
  'X-Title': 'Kinder Denkspiele'
}
```

**Request Body:**
```typescript
{
  model: 'google/gemini-2.5-flash',
  temperature: 1.2,
  max_tokens: 1000,
  response_format: { type: 'json_object' },
  messages: [
    { role: 'system', content: rendered.system_prompt },
    { role: 'user', content: rendered.user_prompt }
  ]
}
```

**Expected Response:**
```json
{
  "type": "riddle",
  "question": "Ich habe 4 Beine und belle. Was bin ich?",
  "options": ["Katze", "Hund", "Vogel", "Maus"],
  "correctIndex": 1,
  "explanation": "Der Hund hat 4 Beine und bellt!",
  "difficulty": 2
}
```

### Content Safety

**Multiple Layers:**

1. **System Prompt:** Strict rules about appropriate content
2. **Banned Words Filter:** Checks response for inappropriate terms
3. **Validation:** Ensures 4 options, valid correctIndex, etc.
4. **Fallback Problems:** Pre-written safe problems if LLM fails
5. **Button-Only UI:** Kids never type, only click buttons

**Banned Words:**
```typescript
const BANNED_WORDS = [
  'tot', 'sterben', 'gewalt', 'blut', 'waffe',
  'krieg', 'terror', 'mord', 'töten', 'schießen'
];
```

---

## 🎮 Game Logic (LogicLabEngine)

**File:** `src/lib/services/logic-lab.service.ts`

### Game Flow

```
1. startGame()
   ├─ Generate first problem (no history)
   ├─ Create session in MongoDB
   └─ Return initial state

2. submitAnswer()
   ├─ Load session
   ├─ Evaluate answer (correct/incorrect)
   ├─ Update score & lives
   ├─ Build performance history (last 5)
   ├─ Generate next problem (with history)
   ├─ Update session in MongoDB
   └─ Return new state OR game over

3. getStats()
   └─ Return problem history + results
```

### State Management

**LogicLabGameState:**
```typescript
{
  initialGuidance: string;           // Adult's input
  modelName: string;                 // 'google/gemini-2.5-flash'
  currentProblem: Problem;           // Active problem
  problemHistory: Problem[];         // All problems (with answers)
  correctAnswers: number;            // Total correct
  consecutiveCorrect: number;        // Current streak
  consecutiveIncorrect: number;      // Current streak
  currentDifficultyLevel: number;    // 1-5 (informational)
  totalProblems: number;             // Always 15
  hintsUsed: number;                 // Future feature
}
```

### Adaptive Difficulty

**How It Works:**

1. **LLM Sees Performance History:**
   - Last 5 problems with questions, types, difficulties, results
   - Consecutive correct/incorrect streaks

2. **LLM Makes Intelligent Decision:**
   ```
   If consecutive_correct >= 2:
     → Increase difficulty ~1 level
   Else if consecutive_incorrect >= 2:
     → Decrease difficulty ~1 level
   Else:
     → Similar difficulty
   ```

3. **LLM Returns Actual Difficulty:**
   - Not hardcoded ±1 level
   - Can make bigger jumps if needed
   - Considers overall pattern, not just last 2 answers

**Example History Passed to LLM:**
```yaml
BISHERIGE PERFORMANCE:
- Frage: "Welches Tier macht 'Wuff'?" (riddle, Level 1) → ✓ Richtig
- Frage: "Was kommt als nächstes? 2, 4, 6, ___" (pattern, Level 2) → ✓ Richtig
- Frage: "Welches passt nicht? Hund, Katze, Auto" (category, Level 3) → ✗ Falsch
- Frage: "Was passiert wenn Eis warm wird?" (cause-effect, Level 2) → ✓ Richtig
- Frage: "Ich bin gelb und leuchte am Tag..." (riddle, Level 2) → ✓ Richtig

ADAPTIVE SCHWIERIGKEIT:
Das Kind löst gerade mehrere Aufgaben richtig! Erhöhe die Schwierigkeit um 1 Level.
```

### Scoring System

| Event | Score | Lives | Notes |
|-------|-------|-------|-------|
| Correct answer | +1 | No change | Add to streak |
| Incorrect answer | 0 | -1 | Reset correct streak |
| Game start | 0 | 3 | 15 questions total |
| Game over | Final | 0 or after Q15 | Whichever comes first |

### Problem Selection

**Type Rotation:**
- Avoid repeating the last problem type
- Random selection from: riddle, pattern, category, cause-effect
- LLM sees what types were used recently

**Repetition Prevention:**
- LLM sees last 5 full questions
- Explicit instruction: "KOMPLETT NEUE Frage"
- Instruction: "Nutze ein anderes Thema als vorher"

---

## 🎨 UI Implementation

**File:** `src/routes/game/logic-lab/+page.svelte`

### Game Phases

```typescript
type GamePhase = 'setup' | 'playing' | 'feedback' | 'gameOver';
```

**Phase Flow:**
```
setup → playing → feedback → playing → feedback → ... → gameOver
  ↓       ↓          ↓ (3s)    ↓          ↓ (3s)           ↓
Input   Show Q    Show result Next Q    Show result    Final score
```

### State Management (Svelte 5 Runes)

```typescript
let gamePhase = $state<GamePhase>('setup');
let sessionId = $state<string>('');
let initialGuidance = $state<string>('');  // Setup phase only

let currentProblem = $state<{
  question: string;
  options: string[];
} | null>(null);

let score = $state<number>(0);
let lives = $state<number>(3);
let round = $state<number>(0);
let totalRounds = $state<number>(15);

let lastAnswerCorrect = $state<boolean>(false);
let explanation = $state<string>('');
let selectedAnswerIndex = $state<number>(-1);

let loading = $state<boolean>(false);
let submitting = $state<boolean>(false);
```

### Key Functions

```typescript
// Phase 1: Setup
async function startGame() {
  const response = await fetch('/api/game/logic-lab/start', {
    method: 'POST',
    body: JSON.stringify({
      userId,
      difficulty,
      initialGuidance: initialGuidance.trim() || undefined
    })
  });

  const data = await response.json();
  sessionId = data.sessionId;
  currentProblem = data.problem;
  // ... set state
  gamePhase = 'playing';
}

// Phase 2: Submit Answer
async function submitAnswer(answerIndex: number) {
  selectedAnswerIndex = answerIndex;

  const response = await fetch('/api/game/logic-lab/answer', {
    method: 'POST',
    body: JSON.stringify({ sessionId, answerIndex })
  });

  const data = await response.json();
  lastAnswerCorrect = data.correct;
  explanation = data.explanation;
  score = data.score;
  lives = data.lives;

  gamePhase = 'feedback';

  // Auto-advance after 3 seconds
  setTimeout(() => {
    if (data.gameOver) {
      gamePhase = 'gameOver';
    } else {
      currentProblem = data.nextProblem;
      selectedAnswerIndex = -1;
      gamePhase = 'playing';
    }
  }, 3000);
}
```

### UI Screens

**1. Setup Screen:**
```svelte
<textarea
  bind:value={initialGuidance}
  placeholder="z.B. 'Mein Kind ist 7 Jahre alt und liebt Tiere'"
  rows="3"
></textarea>
<button onclick={startGame}>Spiel starten! 🚀</button>
```

**2. Playing Screen:**
```svelte
<div class="header">
  Runde {round}/{totalRounds}
  Punkte: {score}
  {'❤️'.repeat(lives)}{'🖤'.repeat(3 - lives)}
</div>

<div class="problem">
  {currentProblem.question}
</div>

<div class="options">
  {#each currentProblem.options as option, index}
    <button onclick={() => submitAnswer(index)}>
      {String.fromCharCode(65 + index)}. {option}
    </button>
  {/each}
</div>
```

**3. Feedback Screen:**
```svelte
{#if lastAnswerCorrect}
  <div class="text-8xl">✅</div>
  <h2>Richtig!</h2>
{:else}
  <div class="text-8xl">❌</div>
  <h2>Nicht ganz...</h2>
{/if}

<div class="explanation">
  {explanation}
</div>

<p>Nächstes Rätsel kommt gleich...</p>
```

**4. Game Over Screen:**
```svelte
<div class="text-8xl">🎉</div>
<h2>Spiel beendet!</h2>

<div class="final-score">
  Deine Punktzahl: {score} / {totalRounds}
</div>

<button onclick={playAgain}>🔄 Nochmal spielen</button>
<button onclick={goHome}>🏠 Zurück</button>
```

---

## 🔌 API Endpoints

### POST /api/game/logic-lab/start

**Description:** Initialize new game, generate first problem

**Request:**
```typescript
{
  userId: string;
  difficulty: 'easy' | 'hard';
  initialGuidance?: string;  // Optional adult input
}
```

**Response (200):**
```typescript
{
  sessionId: string;
  problem: {
    question: string;
    options: string[];  // 4 choices
  };
  score: 0;
  lives: 3;
  round: 1;
  totalRounds: 15;
}
```

**Errors:**
- 400: Missing userId or difficulty
- 500: Failed to start game

---

### POST /api/game/logic-lab/answer

**Description:** Submit answer, get feedback and next problem

**Request:**
```typescript
{
  sessionId: string;
  answerIndex: number;  // 0-3
}
```

**Response (200):**
```typescript
{
  correct: boolean;
  explanation: string;
  nextProblem?: {         // Only if not game over
    question: string;
    options: string[];
  };
  score: number;
  lives: number;
  round: number;
  gameOver: boolean;
  finalScore?: number;    // Only if gameOver = true
}
```

**Errors:**
- 400: Missing sessionId or answerIndex, or invalid index
- 404: Session not found
- 500: Failed to submit answer

---

### GET /api/game/logic-lab/stats

**Description:** Get game statistics and history

**Query Params:** `?sessionId=XXX`

**Response (200):**
```typescript
{
  sessionId: string;
  score: number;
  lives: number;
  totalProblems: number;
  correctAnswers: number;
  problemHistory: Array<{
    question: string;
    type: ProblemType;
    userAnswer: string | null;
    correctAnswer: string;
    isCorrect: boolean;
  }>;
  startedAt: Date;
  endedAt?: Date;
}
```

**Errors:**
- 400: Missing sessionId
- 404: Session not found
- 500: Failed to retrieve stats

---

## 🔄 Modifying Logic Lab

### Changing Prompt Behavior

**Edit:** `src/lib/prompts/generate-problem.yaml`

```yaml
# Adjust creativity
temperature: 1.5  # Higher = more creative (range: 0-2)

# Modify system prompt
system_prompt: |
  Du bist ein freundlicher Lehrer...
  # Add/remove instructions here

# Change user prompt
user_prompt: |
  Erstelle ein neues {{ problem_type }}.
  # Add more context here
```

**No code changes needed!** Just edit YAML and restart server.

---

### Adding New Problem Types

**1. Update Type Definition:**

`src/lib/types/index.ts`:
```typescript
export type ProblemType =
  | 'riddle'
  | 'pattern'
  | 'category'
  | 'cause-effect'
  | 'new-type';  // Add here
```

**2. Update Prompt:**

`src/lib/prompts/generate-problem.yaml`:
```yaml
PROBLEMTYPEN (sei kreativ!):
  - riddle: ...
  - pattern: ...
  - new-type: "Description and example"
```

**3. Update Selection:**

`src/lib/services/logic-lab.service.ts`:
```typescript
const PROBLEM_TYPES: ProblemType[] = [
  'riddle', 'pattern', 'category', 'cause-effect', 'new-type'
];
```

---

### Adjusting Game Length

`src/lib/services/logic-lab.service.ts`:
```typescript
logicLabState: {
  // ...
  totalProblems: 20,  // Change from 15 to any number
  // ...
}
```

---

### Changing LLM Model

**Option 1: Edit YAML**
```yaml
# src/lib/prompts/generate-problem.yaml
model: "anthropic/claude-3-5-sonnet"  # More powerful
# or
model: "openai/gpt-4o"                # Different provider
```

**Option 2: Edit Service**
```typescript
// src/lib/services/logic-lab.service.ts
modelName: 'anthropic/claude-3-5-sonnet',
```

**Available Models:** See [OpenRouter Models](https://openrouter.ai/models)

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Start game with initial guidance → generates relevant problem
- [ ] Start game without guidance → generates age-appropriate problem
- [ ] Answer correctly → see ✅ feedback + explanation
- [ ] Answer incorrectly → lose life, see ❌ + explanation
- [ ] Get 2 correct in a row → next problem is harder
- [ ] Get 2 incorrect in a row → next problem is easier
- [ ] Complete 15 problems → game over screen
- [ ] Lose all 3 lives → early game over
- [ ] Problems don't repeat
- [ ] Each problem has unique theme/topic
- [ ] Difficulty visibly adapts

### Testing with Different Models

```typescript
// Test with Claude (higher quality, slower)
model: "anthropic/claude-3-5-sonnet"

// Test with GPT-4 (different style)
model: "openai/gpt-4o"

// Test with Gemini (fast, good quality)
model: "google/gemini-2.5-flash"  // Current default
```

### Debugging LLM Issues

**Check logs for:**
```typescript
console.error('LLM generation failed:', error);
console.error('Generated problem failed validation');
console.error('Content safety violation:', word);
```

**Common issues:**
- API key invalid → Check `.env` file
- Rate limit → Wait or upgrade OpenRouter plan
- Invalid JSON → LLM not following format (adjust prompt)
- Safety violation → LLM used banned word (falls back automatically)

---

## 💰 Cost Estimation

### Current Configuration

**Model:** Google Gemini 2.5 Flash
**Cost per 1M tokens:**
- Input: ~$0.075
- Output: ~$0.30

**Per Game (15 questions):**
- ~15 API calls
- ~150 input tokens per call (with history)
- ~100 output tokens per call
- **Total:** ~3,750 tokens per game
- **Cost:** ~$0.0015 per game

**1000 Games:** ~$1.50
**10,000 Games:** ~$15

Very affordable for a hobby/educational project!

### Cost Optimization

**Reduce costs:**
1. Use smaller model: `google/gemini-flash-1.5` (cheaper)
2. Reduce history size: Pass 3 problems instead of 5
3. Lower max_tokens: 500 instead of 1000
4. Cache prompts (future OpenRouter feature)

**Increase quality (higher cost):**
1. Use `anthropic/claude-3-5-sonnet` (~10x cost)
2. Use `openai/gpt-4o` (~5x cost)
3. Increase max_tokens for longer explanations

---

## 🚨 Common Issues

### Issue: Questions repeat
**Cause:** Performance history not being passed
**Fix:** Check `generateNextProblem` builds `performanceHistory` array

### Issue: Difficulty doesn't adapt
**Cause:** LLM not seeing streak information
**Fix:** Verify `consecutiveCorrect`/`consecutiveIncorrect` passed to prompt

### Issue: Inappropriate content generated
**Cause:** LLM bypassed safety rules (rare)
**Fix:** Content validator catches it, uses fallback. If persistent, strengthen system prompt.

### Issue: LLM returns invalid JSON
**Cause:** Model not following format
**Fix:**
- Add `response_format: { type: "json_object" }` (already set)
- Strengthen JSON format instructions in prompt
- Add example in system prompt

### Issue: High API costs
**Cause:** Too many tokens per request
**Fix:**
- Reduce `max_tokens` from 1000 to 500
- Shorten performance history from 5 to 3
- Switch to cheaper model

---

## 📖 Related Files

| File | Purpose |
|------|---------|
| `docs/LOGIC-LAB-SPEC.md` | Complete technical specification (15 sections) |
| `docs/LOGIC-LAB.md` | This developer guide |
| `src/lib/prompts/generate-problem.yaml` | LLM prompt template |
| `src/lib/services/prompt-loader.service.ts` | YAML/Jinja2 loader |
| `src/lib/services/llm.service.ts` | OpenRouter integration |
| `src/lib/services/logic-lab.service.ts` | Game engine |
| `src/routes/api/game/logic-lab/` | API endpoints |
| `src/routes/game/logic-lab/+page.svelte` | UI implementation |
| `src/lib/types/index.ts` | Type definitions |

---

## 🎯 Design Decisions

### Why Google Gemini 2.5 Flash?

**Pros:**
- Fast response time (~1-2s)
- Very cheap (~$0.001 per problem)
- High quality structured outputs
- Good German language support
- Follows JSON format reliably

**Alternatives considered:**
- Claude 3.5 Haiku: Similar speed/cost, tried first but switched
- GPT-4o Mini: Good but more expensive
- Claude 3.5 Sonnet: Too expensive for this use case

### Why YAML + Jinja2?

**Pros:**
- Easy prompt iteration (no code changes)
- Clear separation of concerns
- Version control for prompts
- Dynamic content generation
- Industry standard (used by many LLM tools)

**Alternatives considered:**
- Hardcoded strings: Not maintainable
- LangChain: Too heavy for our simple needs
- Custom template engine: Why reinvent the wheel?

### Why 15 Questions?

**Analysis:**
- 5 questions: Too short for meaningful adaptation
- 10 questions: Better but still brief
- **15 questions:** Sweet spot for:
  - Sufficient time to adapt difficulty
  - See performance patterns
  - Not too long for kids (10-15 min)
  - Cost remains very low
- 20+ questions: Risk of fatigue

### Why Temperature 1.2?

**Testing results:**
- 0.7: Too conservative, repetitive themes
- 0.9: Good but some similarity
- **1.2:** High creativity, very diverse problems
- 1.5: Too random, sometimes unclear questions

---

## 🔮 Future Enhancements

### Short Term

- [ ] Display actual difficulty level to user (1-5 stars)
- [ ] Show performance trend graph
- [ ] Add hint system (costs 0 points)
- [ ] Problem categories preferences (more animals vs. numbers)

### Medium Term

- [ ] Image-based problems (use vision models)
- [ ] Voice input for answers
- [ ] Multi-language support (English, French)
- [ ] Parent dashboard to review sessions
- [ ] Achievements/badges system

### Long Term

- [ ] Problem pool pre-generation (100 problems on startup)
- [ ] Collaborative mode (2 kids, taking turns)
- [ ] Custom problem creation (adults write templates)
- [ ] A/B testing different prompts
- [ ] Machine learning difficulty prediction

---

**For AI Agents:** This game is unique in the codebase for using LLM-generated content. When modifying, remember that quality depends heavily on prompt engineering, not code. Start with the YAML file!
