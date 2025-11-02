---
title: "Components Layer Documentation"
purpose: "Reusable UI components built with Svelte 5"
parent: "../../../CLAUDE.md"
last_updated: "2025-11-02"
keywords: ["components", "ui", "svelte-5", "runes", "button", "card", "reusable"]
---

# 🧩 Components Layer - Reusable UI

**Layer:** UI Components
**Location:** `src/lib/components/`
**Parent Guide:** [Main CLAUDE.md](../../../CLAUDE.md) | [Lib CLAUDE.md](../CLAUDE.md)

---

## 🎯 Purpose

Reusable Svelte 5 UI components shared across multiple pages. All components:
- Use Svelte 5 runes syntax
- Follow consistent styling patterns
- Are kid-friendly (large, colorful, clear)
- Use Tailwind CSS v4 utility classes

---

## 📂 Components (8 Total)

### Core UI
- **Button.svelte** - Styled button with variants
- **Card.svelte** - Container component
- **GameStats.svelte** - Score/lives/round display

### Game-Specific
- **VisualMemoryGrid.svelte** - Grid for visual memory game

### Märchenweber-Specific
- **FunNuggetCard.svelte** - Fun fact display card
- **JourneyRecap.svelte** - Story choices history
- **ProgressSteps.svelte** - Visual progress indicator
- **SpeakerButton.svelte** - Text-to-speech button

---

## 🔘 Button Component

**File:** `Button.svelte`

Styled button with variants and sizes for consistent UI.

### Props

```typescript
let {
  variant = 'primary',      // 'primary' | 'secondary' | 'success' | 'danger'
  size = 'md',              // 'sm' | 'md' | 'lg' | 'xl'
  onclick = undefined,      // Click handler
  disabled = false,         // Disabled state
  class: className = '',    // Additional CSS classes
  children                  // Content (Svelte 5 children)
} = $props();
```

### Variants

- **primary**: Gradient purple-pink (default)
- **secondary**: Gradient blue-purple
- **success**: Gradient green-teal (for correct answers)
- **danger**: Gradient red-orange (for incorrect/delete actions)

### Sizes

- **sm**: Small (text-base, px-4 py-2)
- **md**: Medium (text-lg, px-6 py-3) - default
- **lg**: Large (text-xl, px-8 py-4)
- **xl**: Extra large (text-2xl, px-10 py-5)

### Usage

```svelte
<script>
  import Button from '$lib/components/Button.svelte';
  
  function handleClick() {
    console.log('Clicked!');
  }
</script>

<!-- Basic usage -->
<Button onclick={handleClick}>
  Click Me
</Button>

<!-- With variants and sizes -->
<Button variant="success" size="lg" onclick={handleClick}>
  ✅ Correct!
</Button>

<Button variant="danger" size="md" disabled={true}>
  ❌ Disabled
</Button>
```

### Features

- Hover effects (scale transform)
- Active state styling
- Disabled state (cursor-not-allowed, opacity-50)
- Smooth transitions
- Rounded corners
- Shadow effects

---

## 🃏 Card Component

**File:** `Card.svelte`

Container component for content blocks.

### Props

```typescript
let {
  class: className = '',    // Additional CSS classes
  children                  // Content
} = $props();
```

### Default Styling

- White background with transparency
- Rounded corners (rounded-3xl)
- Shadow (shadow-2xl)
- Padding (p-8)
- Backdrop blur for glassmorphism effect

### Usage

```svelte
<script>
  import Card from '$lib/components/Card.svelte';
</script>

<!-- Basic card -->
<Card>
  <h2>Title</h2>
  <p>Content goes here</p>
</Card>

<!-- With custom classes -->
<Card class="max-w-md mx-auto">
  <h2>Centered Card</h2>
</Card>
```

### Customization

Override or extend default classes:

```svelte
<Card class="bg-blue-50">
  <!-- Custom background -->
</Card>
```

---

## 📊 GameStats Component

**File:** `GameStats.svelte`

Displays game statistics (score and lives) with hearts.

### Props

```typescript
let {
  score = 0,          // Current score
  lives = 3,          // Remaining lives
  round = undefined   // Optional: current round number
} = $props();
```

### Usage

```svelte
<script>
  import GameStats from '$lib/components/GameStats.svelte';
  
  let score = $state(5);
  let lives = $state(2);
</script>

<GameStats {score} {lives} />

<!-- With round counter -->
<GameStats {score} {lives} round={3} />
```

### Display

- **Score:** ⭐ Score: X (left side)
- **Round:** 🔄 Runde: X (center, if provided)
- **Lives:** ❤️ hearts (right side, filled/empty based on lives)

### Features

- Responsive layout (flex)
- Large text for readability
- Heart icons (❤️ for alive, 🖤 for lost)
- Centered alignment

---

## 🎯 VisualMemoryGrid Component

**File:** `VisualMemoryGrid.svelte`

Grid component for visual memory game with target highlighting.

### Props

```typescript
let {
  gridSize,               // 3 or 4 (for 3x3 or 4x4)
  targetPositions = [],   // Indices of blue squares
  userSelections = [],    // User's selected indices
  showTargets = false,    // Whether to show targets (during presentation)
  onCellClick = undefined, // Callback: (index: number) => void
  showFeedback = false,   // Show correct/incorrect feedback
  disabled = false        // Disable interaction
} = $props();
```

### Usage

**Presentation Phase:**
```svelte
<VisualMemoryGrid
  gridSize={3}
  targetPositions={[1, 4, 7]}
  showTargets={true}
  disabled={true}
/>
```

**Recall Phase:**
```svelte
<VisualMemoryGrid
  gridSize={3}
  targetPositions={[]}
  userSelections={userSelections}
  onCellClick={handleCellClick}
  showTargets={false}
  disabled={false}
/>
```

**Feedback Phase:**
```svelte
<VisualMemoryGrid
  gridSize={3}
  targetPositions={[1, 4, 7]}
  userSelections={[1, 3, 7]}
  showFeedback={true}
  showTargets={true}
  disabled={true}
/>
```

### Cell States

- **Default:** Gray background
- **Target (during presentation):** Blue background
- **User selection:** Blue border
- **Correct (feedback):** Green background
- **Incorrect (feedback):** Red background

### Features

- Responsive grid layout
- Touch-friendly cell size
- Visual feedback
- Hover effects (when not disabled)
- Smooth transitions

---

## 🎭 Märchenweber Components

**Note:** These components are specific to the Märchenweber storytelling game.

### FunNuggetCard.svelte

Displays fun facts during story generation wait time.

**Props:** `nugget` (string) - The fun fact text

### JourneyRecap.svelte

Shows all previous choices made in the story.

**Props:** `choices` (string[]) - Array of user choices

### ProgressSteps.svelte

Visual progress indicator during async LLM operations.

**Props:** `steps` (array) - Array of {label, status} objects

### SpeakerButton.svelte

Text-to-speech button for reading story text aloud.

**Props:** `text` (string), `voice` (optional)

**See:** [backend/CLAUDE.md](../../../../backend/CLAUDE.md) for Märchenweber details

---

## ✨ Svelte 5 Patterns

### Props Definition

```typescript
// OLD (Svelte 4)
export let variant = 'primary';
export let onclick = undefined;

// NEW (Svelte 5) ✅
let {
  variant = 'primary',
  onclick = undefined,
  children
} = $props();
```

### Children Rendering

```svelte
<!-- OLD (Svelte 4) -->
<slot />

<!-- NEW (Svelte 5) ✅ -->
{@render children()}
```

### Reactive State (if needed in component)

```typescript
let count = $state(0);
let doubled = $derived(count * 2);

$effect(() => {
  console.log('Count changed:', count);
});
```

**See:** [Main CLAUDE.md > Svelte 5 Runes](../../../CLAUDE.md#svelte-5-runes)

---

## 🆕 Creating a New Component

### Step-by-Step

1. **Create file** (`src/lib/components/NewComponent.svelte`)

```svelte
<script lang="ts">
  // Define props
  let {
    text = '',
    onclick = undefined,
    children
  }: {
    text?: string;
    onclick?: () => void;
    children?: any;
  } = $props();
  
  // Local state (if needed)
  let isHovered = $state(false);
  
  // Derived values (if needed)
  let uppercaseText = $derived(text.toUpperCase());
</script>

<div
  class="new-component"
  onmouseenter={() => isHovered = true}
  onmouseleave={() => isHovered = false}
  onclick={onclick}
>
  <p>{uppercaseText}</p>
  {@render children?.()}
</div>

<style>
  /* Component-specific styles if needed */
  .new-component {
    /* Tailwind utility classes are preferred */
  }
</style>
```

2. **Use component**

```svelte
<script>
  import NewComponent from '$lib/components/NewComponent.svelte';
</script>

<NewComponent text="Hello" onclick={() => alert('Clicked!')}>
  <span>Child content</span>
</NewComponent>
```

---

## 🎨 Styling Guidelines

### Use Tailwind Utility Classes

**Preferred:**
```svelte
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <!-- Content -->
</div>
```

**Avoid custom CSS when possible:**
```svelte
<style>
  .custom-box {
    display: flex;
    padding: 1rem;
    /* ... */
  }
</style>
```

### Kid-Friendly Design

- **Large touch targets:** Minimum 48x48px for buttons
- **High contrast:** Easy to read text
- **Bright colors:** Gradients and vibrant colors
- **Clear feedback:** Visual response to interactions
- **Simple layouts:** Not cluttered

**See:** [THEMING.md](../../../THEMING.md)

---

## 🔄 Common Patterns

### Conditional Rendering

```svelte
{#if condition}
  <div>Show when true</div>
{:else}
  <div>Show when false</div>
{/if}
```

### Lists

```svelte
{#each items as item (item.id)}
  <div>{item.name}</div>
{/each}
```

### Event Handling

```svelte
<button onclick={() => handleClick()}>Click</button>
<input oninput={(e) => handleInput(e.target.value)} />
```

---

## 🐛 Common Issues

### Issue: Props not reactive
**Solution:** Use `$props()` syntax, not `export let`

### Issue: Slot not rendering
**Solution:** Use `{@render children()}` instead of `<slot />`

### Issue: Tailwind classes not applying
**Solution:** Check `app.css` has `@import "tailwindcss";`

**See:** [TROUBLESHOOTING.md](../../../TROUBLESHOOTING.md)

---

## 📖 Related Documentation

- [Main CLAUDE.md](../../../CLAUDE.md) - Entry point
- [Lib CLAUDE.md](../CLAUDE.md) - Lib layer overview
- [THEMING.md](../../../THEMING.md) - Styling and customization
- [TECH-STACK.md > Svelte 5](../../../TECH-STACK.md#svelte-5) - Svelte 5 details

---

**All components follow Svelte 5 runes syntax and Tailwind CSS v4 utility-first approach.**

