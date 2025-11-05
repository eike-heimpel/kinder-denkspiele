# Image Generation System Specification

**Version:** 2.0
**Date:** 2025-11-02
**Status:** Implementation in Progress

---

## 🎯 Goals

### Primary Objectives

1. **Better UX**: Show story + choices immediately, generate image asynchronously in background
2. **Special Images**: Make images celebrate the player's choice (reward feeling), not just scene summaries
3. **Visual Consistency**: Characters look the same across all images via persistent descriptions
4. **Controlled Variance**: Add visual variety through RNG while staying scene-appropriate

### User Experience Flow

```
User makes choice
    ↓
Story + choices appear IMMEDIATELY
Image placeholder shows "🎨 Dein Bild wird gemalt..."
    ↓
Background: Image generation starts
    ↓ (2-10 seconds later)
Image appears, celebrating the choice the user made
```

---

## 🏗️ Architecture Changes

### MongoDB Schema Updates

**New Fields in Session Document:**

```javascript
{
  // NEW: Visual style guide (generated once, persisted)
  "style_guide": "Watercolor fairy tale style with soft pastel colors, dreamy magical atmosphere",

  // NEW: Character registry (persistent character descriptions)
  "character_registry": [
    {
      "name": "Princess Luna",
      "description": "7 years old, brown curly hair, purple dress, kind smile",
      "first_seen_round": 1,
      "last_seen_round": 5
    },
    {
      "name": "Wise Fox",
      "description": "red fur, golden eyes, small and friendly",
      "first_seen_round": 2,
      "last_seen_round": 5
    }
  ],

  // NEW: Async image status tracking
  "pending_image": {
    "status": "generating" | "ready" | "failed",
    "round": 5,
    "image_url": null | "data:image/...",
    "started_at": ISODate("2025-11-02T14:30:00Z"),
    "completed_at": ISODate("2025-11-02T14:30:08Z")
  },

  // UPDATED: Image history with choice context
  "image_history": [
    {
      "round": 1,
      "choice_made": "Ich öffne die leuchtende Tür",
      "url": "data:image/...",
      "prompt_used": "Princess Luna opening a glowing door...",
      "characters_in_scene": ["Princess Luna"]
    }
  ],

  // REMOVED: first_image_url, first_image_description, previous_image_url
}
```

### Character Registry System

**Purpose**: Ensure consistent character appearance across all images

**How it works:**

1. **Round 1**: Narrator includes character descriptions in JSON response
2. **Save to MongoDB**: Character registry created and persisted
3. **Round 2+**: Narrator receives existing characters in prompt
4. **Consistency**: Narrator uses exact same names/descriptions for existing characters
5. **New Characters**: Narrator adds new characters with descriptions
6. **Merge**: System merges new characters into registry, updates `last_seen_round`

**Example Flow:**

```
Round 1: Narrator creates "Princess Luna: 7 years old, brown curly hair, purple dress"
         → Saved to character_registry in MongoDB

Round 2: Narrator receives character_registry in prompt
         → Sees "Princess Luna" already exists
         → Returns: {"name": "Princess Luna"} (no new description)
         → Also adds: {"name": "Talking Tree", "description": "ancient oak, glowing eyes"}
         → System merges: Luna unchanged, Tree added to registry

Round 3: Image generation uses registry
         → Princess Luna ALWAYS has "brown curly hair, purple dress"
         → Talking Tree ALWAYS has "ancient oak, glowing eyes"
```

### Style Guide System

**Purpose**: Maintain consistent visual style across all images

**How it works:**

1. **Once at Start**: Generate 1-2 sentence style description
2. **Save to MongoDB**: Persisted in session document
3. **Every Image**: Include style guide in image generation prompt
4. **No Previous Image Feeding**: Style comes from text description, not image input

**Example Style Guides:**

- "Watercolor fairy tale style with soft pastel colors, dreamy magical atmosphere, whimsical storybook illustrations"
- "Digital art with vibrant colors, magical fantasy atmosphere, child-friendly cartoon style"
- "Soft pencil sketch style with gentle colors, cozy storybook feel, warm and inviting"

---

## 🎨 Image Generation Pipeline

### Old System (v1.0)

```
1. Narrator generates story + image_prompt (German)
2. Scene analyzer determines intensity/perspective/lighting
3. Translator converts to English with variation parameters
4. Feed previous_image_url for character consistency
5. Generate image
6. Wait for image before returning response
```

### New System (v2.0)

```
1. Narrator generates story + 3 choices + characters_in_scene
2. Return response IMMEDIATELY (no image yet)
3. Background task starts:
   a. Extract choice made from user input
   b. Generate choice-specific image prompt
      - "Princess Luna opening a glowing door, golden light streaming..."
   c. Scene analyzer determines intensity (1-5)
   d. RNG selects variance within scene-appropriate bounds:
      - Perspective: random choice from ["wide shot", "close-up", "eye-level", etc.]
      - Lighting: random from intensity-appropriate pool
      - Framing: random choice from ["centered", "rule of thirds", etc.]
   e. Build final prompt:
      - Choice-specific action
      - Style guide (from MongoDB)
      - Character descriptions (from MongoDB registry)
      - RNG variance parameters
   f. Generate image (NO previous image input)
   g. Save to MongoDB with status "ready"
4. Frontend polls every 2 seconds, shows image when ready
```

---

## 🎲 RNG Variance System

### Scene-Aware Variance

Images should vary visually but stay appropriate to the scene's mood.

**Config Structure:**

```yaml
image_variance:
  perspectives:
    - "wide shot"
    - "close-up"
    - "eye-level view"
    - "low-angle view"
    - "overhead view"
    - "side view"

  lighting_by_intensity:
    low:  # Intensity 1-2 (calm scenes)
      - "soft daylight"
      - "golden hour"
      - "dawn light"
    medium:  # Intensity 3 (moderate scenes)
      - "soft daylight"
      - "moonlight"
      - "sunset"
    high:  # Intensity 4-5 (exciting scenes)
      - "dramatic lighting"
      - "magical glow"
      - "stormy atmosphere"

  framing:
    - "centered composition"
    - "rule of thirds"
    - "character focus"
    - "action moment"
```

**Selection Logic:**

```python
import random

# Scene analyzer determines intensity
intensity = scene_analysis.get("intensity_level", 3)

# Select lighting based on intensity
if intensity <= 2:
    lighting_pool = config.lighting_by_intensity.low
elif intensity <= 3:
    lighting_pool = config.lighting_by_intensity.medium
else:
    lighting_pool = config.lighting_by_intensity.high

# Random selection
perspective = random.choice(config.perspectives)
lighting = random.choice(lighting_pool)
framing = random.choice(config.framing)
```

---

## 🔄 Async Image Generation

### API Flow

**1. Turn Request (Frontend → Backend)**

```http
POST /api/game/maerchenweber/turn
{
  "session_id": "...",
  "choice_text": "Ich öffne die leuchtende Tür"
}
```

**2. Immediate Response (Backend → Frontend)**

```json
{
  "story_text": "Du öffnest die Tür...",
  "choices": ["Ich...", "Ich...", "Ich...", "Ich..."],
  "fun_nugget": "Wusstest du? ...",
  "image_url": null,  // No image yet!
  "round_number": 2
}
```

**3. Background Task Starts**

```python
asyncio.create_task(
    _generate_and_save_image(
        session_id=session_id,
        choice_made="Ich öffne die leuchtende Tür",
        story_text=story_text,
        style_guide=style_guide,
        character_registry=character_registry,
        current_round=2
    )
)
```

**4. Frontend Polls for Image**

```http
GET /api/game/maerchenweber/image/{session_id}
```

**5. Polling Response**

```json
// Still generating
{
  "status": "generating",
  "round": 2,
  "image_url": null
}

// Ready!
{
  "status": "ready",
  "round": 2,
  "image_url": "data:image/png;base64,..."
}

// Failed
{
  "status": "failed",
  "round": 2,
  "error": "Image generation timeout"
}
```

**6. Frontend Updates**

```typescript
// Poll every 2 seconds
setInterval(async () => {
  const response = await fetch(`/api/game/maerchenweber/image/${sessionId}`);
  const data = await response.json();

  if (data.status === "ready" && data.image_url) {
    currentImageUrl = data.image_url;
    clearInterval(pollInterval);
  }
}, 2000);

// Timeout after 30 seconds
setTimeout(() => {
  if (!currentImageUrl) {
    imageError = true;
    clearInterval(pollInterval);
  }
}, 30000);
```

---

## 🎭 Choice-Based Image Prompts

### Philosophy

**Old**: "Here's what the scene looks like"
**New**: "Here's you doing the awesome thing you chose!"

### Examples

**Choice**: "Ich öffne die leuchtende Tür"

**Old Image Prompt**:
- "A glowing door in a magical forest"

**New Image Prompt**:
- "Princess Luna reaching out to open a glowing wooden door, golden light streaming through the cracks, her face filled with wonder and excitement as the magical light illuminates her"

**Choice**: "Ich spreche mit dem Fuchs"

**Old Image Prompt**:
- "A wise fox in the forest"

**New Image Prompt**:
- "Princess Luna kneeling down to speak with a wise red fox, their eyes meeting in understanding, surrounded by soft moonlight filtering through trees"

### Prompt Generation Process

```python
# 1. Generate choice-specific prompt
choice_prompt = await llm.generate_text(
    prompt=f"""
    Create an image prompt celebrating this action:

    Action: {choice_made}
    Story: {story_text}
    Characters: {character_descriptions}

    Show the character performing this exact action.
    Make it feel special and rewarding!
    """,
    model="choice_image_generator"
)

# 2. Add variance + style + characters
final_prompt = f"""
{choice_prompt}

Style: {style_guide}
Characters: Princess Luna: 7 years old, brown curly hair, purple dress
Perspective: {random_perspective}
Lighting: {random_lighting}
Framing: {random_framing}
"""

# 3. Generate image (no previous image input!)
image_url = await llm.generate_image(prompt=final_prompt)
```

---

## 📋 Implementation Checklist

### Backend (Python/FastAPI)

- [x] Add prompts to `config.yaml`
  - [x] `style_guide_generator`
  - [x] `choice_image_generator`
  - [x] Update `narrator` with character tracking
  - [x] Update `character_creation` with character extraction
- [x] Add RNG variance config to `config.yaml`
- [x] Add new models to `config.yaml`
- [x] Update LLM service JSON schema for `characters_in_scene`
- [x] Create character_manager.py service
  - [x] `extract_characters_from_response()`
  - [x] `merge_characters()`
  - [x] `get_character_descriptions()`
  - [x] `format_for_prompt()`
- [x] Create image_generator.py service
  - [x] `generate_choice_based_image()` (async background task)
  - [x] `_generate_choice_prompt()`
  - [x] `_analyze_scene_intensity()`
  - [x] `get_random_variance()`
  - [x] `_build_final_prompt()`
- [x] Refactor game_engine.py
  - [x] `_generate_style_guide()`
  - [x] Extract and merge characters using CharacterManager
  - [x] Launch async image generation with asyncio.create_task()
  - [x] Return responses with image_url=None for rounds 2+
- [x] Update `start_adventure()` in `game_engine.py`
  - [x] Generate style guide
  - [x] Extract characters from narrator
  - [x] Create session with new fields (style_guide, character_registry, etc.)
  - [x] Generate Round 1 image (blocking, per user preference)
  - [x] Return with image_url for Round 1
- [x] Update `process_turn()` in `game_engine.py`
  - [x] Load character_registry and style_guide from MongoDB
  - [x] Pass character_registry to narrator prompt
  - [x] Extract and merge characters
  - [x] Save updated registry to MongoDB
  - [x] Launch async image generation (fire and forget)
  - [x] Return with image_url=None
- [x] Add config loader method for image variance
  - [x] `get_image_variance()` in `config_loader.py`
- [x] Add new API endpoints
  - [x] `GET /adventure/image/{session_id}/{round}` in `adventure.py`
  - [x] Update `GET /adventure/user/{user_id}/sessions` to use image_history

### Frontend (SvelteKit)

- [ ] Add SvelteKit proxy endpoint
  - [ ] `src/routes/api/game/maerchenweber/image/[sessionId]/+server.ts`
- [ ] Update game page (`play/+page.svelte`)
  - [ ] Add image state variables (`imageLoading`, `imageError`)
  - [ ] Add polling logic (`pollForImage()`)
  - [ ] Add timeout logic (30 seconds)
  - [ ] Update UI for loading/error/ready states
  - [ ] Add retry button for failed images
  - [ ] Cleanup on unmount

### Testing

- [ ] Test character persistence across multiple rounds
- [ ] Test style guide consistency
- [ ] Test async image delivery (polling works)
- [ ] Test timeout behavior (30 seconds)
- [ ] Test error handling (image generation fails)
- [ ] Test RNG variance (images look different)
- [ ] Test scene-appropriate variance (calm vs exciting scenes)
- [ ] Test choice-specific prompts (images match choices)

---

## 🔍 Success Criteria

### UX Improvements

✅ Story appears within 2-3 seconds (no wait for image)
✅ Image appears within 10 seconds on average
✅ Timeout shows helpful error after 30 seconds
✅ Retry button works when images fail

### Image Quality

✅ Images celebrate the player's choice (not just scene summary)
✅ Characters look consistent across images
✅ Visual style stays consistent (style guide)
✅ Images have variety (different perspectives, lighting, framing)
✅ Variance is scene-appropriate (calm scenes = soft lighting)

### Technical

✅ MongoDB persistence works (character_registry, style_guide)
✅ Async image generation doesn't block responses
✅ Polling works reliably
✅ No memory leaks from polling intervals
✅ Error states handled gracefully

---

## 🚀 Future Enhancements

### Potential Improvements

- **Image caching**: Store generated images in CDN for faster loading
- **Progressive loading**: Show low-res preview while full image generates
- **Multiple styles**: Let users choose different art styles at start
- **Image collections**: Gallery of all images from a story
- **Print feature**: Export story + images as PDF
- **Character evolution**: Characters can change appearance over story (growth, clothing changes)
- **Dynamic style**: Style can evolve based on story mood (start bright, become darker if story gets spooky)

---

## 📝 Notes

### Design Decisions

**Why no previous image feeding?**
- More variance between images (feel more special/unique)
- Character consistency comes from text descriptions instead
- Text descriptions are more reliable than visual matching
- Allows for better RNG variance without style drift

**Why async image generation?**
- Better UX (no waiting for story)
- Images are rewards, not blockers
- Allows time for higher quality generation
- Enables longer timeouts without impacting gameplay

**Why character registry?**
- Single source of truth for character appearance
- Persisted in MongoDB for reliability
- Can be updated/refined across story
- Enables character re-use across different stories (future)

**Why scene-aware RNG?**
- Variance without chaos
- Lighting appropriate to mood
- Best of both worlds (smart + random)

### Data Format

**Current format:**
- Sessions use `turns[]` array with atomic turn objects
- Each turn contains: round, choice_made, story_text, choices, image_url, fun_nugget, timestamps
- Old sessions with `history[]` format are no longer supported

**Note:** Old sessions must be manually migrated in MongoDB or users should start new stories

---

**End of Specification**
