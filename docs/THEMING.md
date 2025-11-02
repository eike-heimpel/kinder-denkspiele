---
title: "Design System & Theming Guide"
purpose: "Formalized design system documentation"
audience: "AI agents, developers, designers"
last_updated: "2025-11-02"
keywords: ["design-system", "theming", "colors", "gradients", "tailwind-v4", "design-tokens", "styling", "ui"]
related_docs: ["CLAUDE.md", "src/lib/components/CLAUDE.md", "TECH-STACK.md"]
---

# 🎨 Design System & Theming Guide

**Last Updated:** 2025-11-02
**Design Tokens:** `src/lib/design-tokens.ts`
**Tailwind Config:** `src/app.css` (@theme block)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Design Tokens](#design-tokens)
- [Color Palette](#color-palette)
- [Button Variants](#button-variants)
- [Component Patterns](#component-patterns)
- [Spacing & Layout](#spacing--layout)
- [Typography](#typography)
- [Animations & Effects](#animations--effects)
- [Usage Examples](#usage-examples)
- [Customization Guide](#customization-guide)

---

## Overview

Kinder Denkspiele uses a **formalized design system** with centralized tokens for consistency. The system is optimized for **kids aged 4-10** with:

- ✨ Bright, vibrant gradients (purple-pink-blue palette)
- 🎯 Large touch targets (48px+ for buttons)
- 🌈 High contrast for readability
- 💫 Smooth, playful animations
- 😊 Emoji-first visual language

**Architecture:**
```
src/app.css (@theme)          ← Tailwind v4 CSS variables
    ↓
src/lib/design-tokens.ts      ← TypeScript design tokens
    ↓
src/lib/components/*.svelte   ← UI components
```

---

## Design Tokens

**File:** `src/lib/design-tokens.ts`

The source of truth for all design values. Import and use throughout the app:

```typescript
import { tokens, components, combine } from '$lib/design-tokens';

// Use individual tokens
const cardClass = `${tokens.spacing.card.padding} ${tokens.radius.card}`;

// Or use predefined combinations
const cardClass = components.gameCard;
```

### Token Structure

```typescript
tokens = {
  colors: { brand, games },
  gradients: { background, navbar, buttons },
  spacing: { card, button, container },
  typography: { heading, body, button, emoji },
  radius: { card, button, input },
  shadows: { card, button, navbar, text },
  effects: { buttonHover, cardHover, blur, fadeIn },
  borders: { card, button },
  zIndex: { navbar, modal, dropdown }
}
```

---

## Color Palette

### Brand Colors (Purple-Pink-Blue)

**Defined in:** `src/app.css` (@theme) and `design-tokens.ts`

```typescript
colors.brand = {
  purple: '#c084fc',      // purple-400
  purpleDark: '#a855f7',  // purple-500
  pink: '#f472b6',        // pink-400
  pinkDark: '#ec4899',    // pink-500
  blue: '#60a5fa',        // blue-400
  blueDark: '#3b82f6'     // blue-500
}
```

**Main Background Gradient:**
```css
bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400
```

### Game-Specific Colors

Each game has a semantic color scheme:

| Game | Light Background | Border | Text |
|------|------------------|--------|------|
| **Verbal Memory** | `from-purple-50 to-pink-50` | `border-purple-200` | `text-purple-700` |
| **Visual Memory** | `from-blue-50 to-indigo-50` | `border-blue-200` | `text-blue-700` |
| **Reaction Time** | `from-orange-50 to-red-50` | `border-orange-200` | `text-orange-700` |
| **Logic Lab** | `from-green-50 to-teal-50` | `border-green-200` | `text-green-700` |
| **Märchenweber** | `from-amber-50 to-yellow-50` | `border-amber-200` | `text-amber-700` |

**Usage:**
```typescript
import { tokens } from '$lib/design-tokens';

<div class={`bg-gradient-to-br ${tokens.colors.games.verbal.light}`}>
```

---

## Button Variants

**File:** `src/lib/components/Button.svelte`

### Variant Reference

| Variant | Use Case | Gradient | Text |
|---------|----------|----------|------|
| **primary** | Main actions, continue | `from-blue-500 to-cyan-500` | White |
| **secondary** | Back, cancel, secondary nav | `bg-white/95` | Purple |
| **success** | Easy difficulty, correct answers | `from-green-500 to-emerald-500` | White |
| **danger** | Hard difficulty, wrong answers | `from-red-500 to-rose-500` | White |
| **warning** | Special actions (Märchenweber) | `from-purple-600 to-pink-600` | White |

### Button Sizes

```typescript
tokens.spacing.button = {
  sm: 'px-6 py-3',   // text-base
  md: 'px-8 py-4',   // text-lg (default)
  lg: 'px-10 py-5',  // text-xl
  xl: 'px-14 py-7'   // text-3xl
}
```

### Usage Example

```svelte
<script>
  import Button from '$lib/components/Button.svelte';
</script>

<Button variant="success" size="lg" onclick={handleClick}>
  ✅ Richtig!
</Button>
```

---

## Component Patterns

### Game Card

**Predefined:** `components.gameCard`

```typescript
// Combines:
tokens.radius.card              // rounded-3xl
tokens.spacing.card.padding     // p-8
tokens.spacing.card.margin      // mb-6
tokens.borders.card             // border-4
tokens.shadows.card             // shadow-lg hover:shadow-xl
tokens.effects.cardHover        // transition-all duration-300
```

**Usage:**
```svelte
<div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-8 mb-6 border-4 border-purple-200 shadow-lg hover:shadow-xl transition-all duration-300">
  <!-- Game card content -->
</div>
```

### Navigation Bar

**Predefined:** `components.navbar`

```typescript
// Gradient background
tokens.gradients.navbar
// = bg-gradient-to-r from-purple-500/80 via-pink-500/80 to-blue-500/80

// With backdrop blur
tokens.effects.blur.md  // backdrop-blur-md
```

**Nav Button Style:**
```css
bg-gradient-to-r from-white/90 to-white/95
hover:from-white hover:to-white
text-purple-700
shadow-lg hover:shadow-xl
transform hover:scale-105
```

### Card Component

**File:** `src/lib/components/Card.svelte`

```svelte
<div class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl p-4 border-2 border-white/50">
  {@render children()}
</div>
```

**Customization:**
- Opacity: `bg-white/95` → `bg-white/80` (more transparent)
- Blur: `backdrop-blur-sm` → `backdrop-blur-md` (more blur)
- Padding: `p-4` → `p-8` (more space)

---

## Spacing & Layout

### Container Spacing

```typescript
tokens.spacing.container = {
  padding: 'p-2',          // Page padding
  topPadding: 'pt-14',     // Account for fixed navbar
  maxWidth: 'max-w-4xl'    // Content max width
}
```

**Page Layout Pattern:**
```svelte
<div class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-2">
  <div class="max-w-4xl mx-auto pt-14">
    <!-- Content -->
  </div>
</div>
```

### Card Spacing

```typescript
tokens.spacing.card = {
  padding: 'p-8',    // Inner padding
  margin: 'mb-6',    // Bottom margin
  inner: 'mb-6',     // Space between card sections
  gap: 'gap-4'       // Gap between buttons
}
```

---

## Typography

### Headings

```typescript
tokens.typography.heading = {
  xl: 'text-3xl font-black',   // Page titles
  lg: 'text-2xl font-black',   // Section titles
  md: 'text-xl font-bold',     // Subsections
  sm: 'text-lg font-bold'      // Small headings
}
```

### Emoji Sizes

```typescript
tokens.typography.emoji = {
  sm: 'text-2xl',  // Inline icons
  md: 'text-3xl',  // Button icons
  lg: 'text-4xl',  // Card icons (old size)
  xl: 'text-5xl'   // Card icons (new size, more impact)
}
```

**Example:**
```svelte
<!-- Game card icon -->
<span class="text-5xl mb-3 inline-block">🗣️</span>

<!-- Button icon -->
<span class="text-3xl">✨</span>
```

---

## Animations & Effects

### Button Effects

```typescript
tokens.effects.buttonHover =
  'transition-all duration-300 transform hover:scale-105 active:scale-95'
```

**Disabled state:**
```css
disabled:opacity-50
disabled:cursor-not-allowed
disabled:hover:scale-100
```

### Card Effects

```typescript
tokens.effects.cardHover = 'transition-all duration-300'
tokens.shadows.card = 'shadow-lg hover:shadow-xl'
```

### Background Gradient Animation

**Custom animation in `+page.svelte`:**

```css
<style>
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 15s ease infinite;
}
</style>
```

### Glassmorphism Effect

```typescript
tokens.effects.blur = {
  sm: 'backdrop-blur-sm',   // Subtle blur
  md: 'backdrop-blur-md',   // Medium blur (navbar)
  lg: 'backdrop-blur-lg'    // Strong blur
}
```

**Usage:**
```svelte
<div class="bg-white/95 backdrop-blur-md">
  <!-- Glass effect -->
</div>
```

---

## Usage Examples

### Creating a New Game Card

```svelte
<script>
  import Button from '$lib/components/Button.svelte';
  import { tokens } from '$lib/design-tokens';
</script>

<div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-8 mb-6 border-4 border-purple-200 hover:border-purple-300 transition-all duration-300 shadow-lg hover:shadow-xl">
  <div class="text-center mb-6">
    <span class="text-5xl mb-3 inline-block">🎮</span>
    <h3 class="text-2xl font-black text-purple-700 mb-3">
      New Game
    </h3>
    <p class="text-base text-gray-700 font-medium">
      Description of the game
    </p>
  </div>

  <div class="flex gap-4 justify-center flex-wrap mt-4">
    <Button variant="success" size="lg" onclick={startEasy}>
      <div class="flex items-center gap-2">
        <span class="text-3xl">🟢</span>
        <span>Einfach</span>
      </div>
    </Button>
    <Button variant="danger" size="lg" onclick={startHard}>
      <div class="flex items-center gap-2">
        <span class="text-3xl">🔴</span>
        <span>Schwer</span>
      </div>
    </Button>
  </div>
</div>
```

### Using Design Tokens Programmatically

```svelte
<script>
  import { tokens, components, combine } from '$lib/design-tokens';

  // Combine multiple token classes
  const myCardClass = combine(
    tokens.radius.card,
    tokens.spacing.card.padding,
    tokens.shadows.card
  );

  // Or use predefined combinations
  const standardCard = components.gameCard;
</script>

<div class={myCardClass}>
  <!-- Content -->
</div>
```

---

## Customization Guide

### Changing the Color Palette

**1. Update Tailwind v4 @theme** (`src/app.css`)

```css
@theme {
  /* Change brand colors */
  --color-brand-purple: #8b5cf6;  /* New purple */
  --color-brand-pink: #ec4899;    /* New pink */
  --color-brand-blue: #3b82f6;    /* New blue */
}
```

**2. Update Design Tokens** (`src/lib/design-tokens.ts`)

```typescript
colors: {
  brand: {
    purple: '#8b5cf6',
    pink: '#ec4899',
    blue: '#3b82f6'
  }
}
```

**3. Update Gradients Throughout**

Search and replace:
- `from-purple-400` → `from-purple-500`
- `via-pink-400` → `via-pink-500`
- `to-blue-400` → `to-blue-500`

### Adding a New Button Variant

**1. Update Button Component** (`src/lib/components/Button.svelte`)

```typescript
interface Props {
  variant?: "primary" | "secondary" | "success" | "danger" | "warning" | "info";  // Add "info"
  // ...
}

const variants = {
  // ... existing variants
  info: "bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg hover:shadow-xl",
};
```

**2. Update Design Tokens** (optional, for documentation)

```typescript
gradients: {
  buttons: {
    // ... existing
    info: 'from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600'
  }
}
```

### Creating Theme Presets

#### Ocean Theme
```typescript
gradients: {
  background: 'bg-gradient-to-br from-blue-400 via-cyan-400 to-teal-400',
  navbar: 'bg-gradient-to-r from-blue-500/80 via-cyan-500/80 to-teal-500/80'
}
```

#### Sunset Theme
```typescript
gradients: {
  background: 'bg-gradient-to-br from-orange-400 via-red-400 to-pink-400',
  navbar: 'bg-gradient-to-r from-orange-500/80 via-red-500/80 to-pink-500/80'
}
```

#### Forest Theme
```typescript
gradients: {
  background: 'bg-gradient-to-br from-green-400 via-emerald-400 to-teal-400',
  navbar: 'bg-gradient-to-r from-green-500/80 via-emerald-500/80 to-teal-500/80'
}
```

---

## Design Principles

### Kid-Friendly UX

✅ **Do:**
- Use bright, vibrant colors
- Large touch targets (min 48px)
- Plenty of emojis for visual learning
- High contrast text (4.5:1 minimum)
- Smooth, playful animations
- Clear visual feedback

❌ **Don't:**
- Dull or muted colors
- Small buttons or text
- Cluttered layouts
- Jarring animations
- Low contrast color combinations

### Performance

✅ **Best Practices:**
- Use `transform` for animations (GPU accelerated)
- Limit simultaneous animations
- Use `will-change` sparingly
- Optimize gradient usage

❌ **Avoid:**
- Animating `position` or `width/height` directly
- Too many backdrop-blur effects
- Excessive shadow usage

### Accessibility

✅ **Guidelines:**
- Maintain WCAG AA contrast ratios (4.5:1 text, 3:1 UI)
- Don't rely solely on color (use icons + text)
- Support keyboard navigation
- Test with screen readers
- Provide clear focus states

---

## Quick Reference

### Common Class Patterns

```css
/* Page background */
min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400

/* Game card */
bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-8 mb-6 border-4 border-purple-200 shadow-lg hover:shadow-xl

/* Button hover */
transition-all duration-300 transform hover:scale-105 active:scale-95

/* Glass effect */
bg-white/95 backdrop-blur-sm

/* Gradient text */
bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent
```

---

## Related Documentation

- **[CLAUDE.md](../CLAUDE.md)** - Main documentation entry point
- **[design-tokens.ts](../src/lib/design-tokens.ts)** - Design token source code
- **[Button.svelte](../src/lib/components/Button.svelte)** - Button component
- **[TECH-STACK.md](./TECH-STACK.md)** - Tailwind v4 details

---

**For questions or customization help, refer to:**
- Tailwind CSS v4 Docs: https://tailwindcss.com/docs
- Design Tokens: `src/lib/design-tokens.ts`
- This guide: `docs/THEMING.md`
