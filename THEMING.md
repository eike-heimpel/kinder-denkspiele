# 🎨 Theming Guide

## Overview

The app uses a centralized theme system located in `src/lib/theme.ts` that makes it easy to customize colors, gradients, animations, and more across the entire application.

## Theme Structure

```typescript
export const theme = {
    colors: { ... },      // Color palettes
    gradients: { ... },   // Gradient definitions
    shadows: { ... },     // Shadow styles
    animations: { ... },  // Animation classes
    spacing: { ... },     // Padding/margin/gap
    text: { ... },        // Text sizes and weights
    borders: { ... },     // Border radius and width
    transitions: { ... }, // Transition timings
};
```

## Quick Customization Examples

### Change Primary Colors

Edit `src/lib/theme.ts`:

```typescript
colors: {
    primary: {
        500: '#0ea5e9',  // Change this to your color
        600: '#0284c7',  // Darker version
        // etc...
    }
}
```

### Change Background Gradients

```typescript
gradients: {
    home: 'from-purple-400 via-pink-400 to-blue-400',  // Home page
    game: 'from-indigo-500 via-purple-500 to-pink-500', // Game page
}
```

### Customize Animations

Animations are defined in component `<style>` sections. Key animations:

#### Word Appearance (`game/verbal-memory/+page.svelte`)
```css
@keyframes wordAppear {
    0% {
        opacity: 0;
        transform: scale(0.5) translateY(-30px);
    }
    100% {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
```

#### Floating Effect
```css
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
```

### Change Button Styles

Buttons use gradient backgrounds. Edit `src/lib/components/Button.svelte`:

```typescript
const variants = {
    primary: "bg-gradient-to-r from-blue-500 to-cyan-500 ...",
    success: "bg-gradient-to-r from-green-500 to-emerald-500 ...",
    danger: "bg-gradient-to-r from-red-500 to-rose-500 ...",
};
```

### Modify Card Appearance

Cards use a glass-morphism effect. Edit `src/lib/components/Card.svelte`:

```html
<div class="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border-4 border-white/50">
```

**Customization options:**
- `bg-white/95` → Change opacity (0-100)
- `rounded-3xl` → Change border radius (sm, md, lg, xl, 2xl, 3xl)
- `shadow-2xl` → Change shadow intensity (sm, md, lg, xl, 2xl)
- `border-4` → Change border width (0, 2, 4, 8)

## Component-Specific Styling

### GameStats Component

Located in `src/lib/components/GameStats.svelte`:

```html
<div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 border-2 border-purple-200">
```

**Key elements:**
- Trophy emoji: `text-purple-700 text-3xl`
- Score number: `text-4xl bg-gradient-to-r from-purple-600 to-pink-600`
- Hearts: Scale and grayscale effects for lost lives

### Home Page

Main gradient background:
```html
<div class="bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 animate-gradient">
```

Brain emoji animation:
```html
<span class="text-9xl animate-bounce-slow">🧠</span>
```

### Game Page

Background:
```html
<div class="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 animate-gradient">
```

Word display with gradient text:
```html
<p class="text-8xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
```

## Tailwind CSS Customization

The app uses Tailwind CSS. You can customize the entire design system in `tailwind.config.js` (if you create one) or directly in the classes.

### Common Tailwind Patterns Used

#### Gradient Text
```html
bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent
```

#### Gradient Background
```html
bg-gradient-to-br from-blue-400 to-cyan-500
```

#### Glass-morphism
```html
bg-white/95 backdrop-blur-sm
```

#### Hover Effects
```html
hover:scale-105 active:scale-95 transition-all duration-300
```

#### Shadows
```html
shadow-lg hover:shadow-xl
```

## Animation Durations

All animations use consistent timing:
- **Fast**: 150ms (quick interactions)
- **Normal**: 300ms (button hovers, transitions)
- **Slow**: 500ms (page transitions)
- **Continuous**: 3s (floating), 15s (gradient backgrounds)

## Emoji Sizes

Emojis are used throughout for kid-friendly appeal:
- Small icons: `text-3xl` (48px)
- Medium icons: `text-5xl` (48px)
- Large icons: `text-7xl` (72px)
- Extra large: `text-9xl` (128px)

## Changing the Overall Color Scheme

To change from purple/pink to a different color scheme:

1. **Choose your palette** (e.g., blue/green)
2. **Update gradients in pages:**
   - Home: `+page.svelte` → `from-blue-400 via-green-400 to-teal-400`
   - Game: `game/verbal-memory/+page.svelte` → `from-blue-500 via-teal-500 to-green-500`
3. **Update component accents:**
   - GameStats: `from-blue-50 to-green-50`, `border-blue-200`
   - Button variants: Use your new color scheme
4. **Update gradient text:**
   - Replace `from-purple-600 to-pink-600` with `from-blue-600 to-green-600`

## Tips for Customization

### Keep it Kid-Friendly
- Use bright, vibrant colors
- Large text and buttons
- Plenty of emojis
- Smooth, playful animations
- High contrast for readability

### Performance
- Avoid too many simultaneous animations
- Keep gradient animations to backgrounds only
- Use `transform` instead of position changes
- Enable GPU acceleration with `transform: translateZ(0)` if needed

### Accessibility
- Maintain color contrast ratios (WCAG AA: 4.5:1 for text)
- Don't rely solely on color (use icons too)
- Keep animations smooth (avoid jarring movements)
- Test on different screen sizes

## Quick Theme Presets

### Ocean Theme
```typescript
gradients: {
    home: 'from-blue-400 via-cyan-400 to-teal-400',
    game: 'from-blue-500 via-cyan-500 to-teal-500',
}
```

### Sunset Theme
```typescript
gradients: {
    home: 'from-orange-400 via-red-400 to-pink-400',
    game: 'from-orange-500 via-red-500 to-pink-500',
}
```

### Forest Theme
```typescript
gradients: {
    home: 'from-green-400 via-emerald-400 to-teal-400',
    game: 'from-green-500 via-emerald-500 to-teal-500',
}
```

### Rainbow Theme
```typescript
gradients: {
    home: 'from-red-400 via-yellow-400 via-green-400 via-blue-400 to-purple-400',
    game: 'from-red-500 via-yellow-500 via-green-500 via-blue-500 to-purple-500',
}
```

## Need Help?

Check the Tailwind CSS documentation: https://tailwindcss.com/docs

All color names and utilities follow Tailwind's conventions.
