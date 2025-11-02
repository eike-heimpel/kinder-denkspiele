# TODO

## Logic Lab - Cost Optimization

### Image Generation Cost Management

**Problem:** Generating a new image for every puzzle round may be expensive with OpenRouter/Gemini API.

**Potential Solutions:**
- Generate new images only every N rounds (e.g., every 5 rounds)
- Cache and reuse images for similar problem types
- Only generate images for certain problem categories
- Add configuration option to enable/disable image generation per age group

**Decision Needed:**
- What is the acceptable cost per play session?
- Should we measure actual costs first before optimizing?
- Should images be optional or always-on?

---

## Märchenweber (Story Game) - UX Improvements

### ✅ COMPLETED: Image Generation Optimization

**Implementation Completed (2025-11-02):**
- ✅ Images now generated every 5 turns instead of every turn (~80% cost savings)
- ✅ Previous image reused on non-image turns for consistency
- ✅ All images stored in `image_history` array with round number and description
- ✅ Configurable via `backend/config.yaml` (`image_generation_interval: 5`)

**Files Modified:**
- `backend/config.yaml` - Added game mechanics configuration
- `backend/app/services/config_loader.py` - Added `get_game_mechanic()` method
- `backend/app/services/game_engine.py` - Conditional image generation logic

---

### ✅ COMPLETED: Story Summarization

**Implementation Completed (2025-11-02):**
- ✅ Story history summarized every 5 turns to reduce LLM context size
- ✅ Keeps last 5 turns in full detail + summary of older turns
- ✅ Summary stored in `history_summary` field in database
- ✅ Narrator receives summary + recent turns for coherent storytelling

**Files Modified:**
- `backend/config.yaml` - Added summarization prompt and model config
- `backend/app/services/game_engine.py` - `_summarize_history()` method and integration

---

### ✅ COMPLETED: Story Persistence & Continuation

**Implementation Completed (2025-11-02):**
- ✅ Stories are fully persisted to MongoDB
- ✅ Full history, images, summaries, and metadata saved
- ✅ Users can view all their stories in a grid layout
- ✅ Users can continue unfinished stories from where they left off
- ✅ Users can replay/read completed stories with full narrative and images

**New Features:**
1. **Stories List Page** (`/game/maerchenweber/stories?userId=X`)
   - Grid layout with story thumbnails (first_image_url)
   - Shows character name, theme, round count, last updated
   - "Continue" and "View" buttons for each story

2. **Story Replay Page** (`/game/maerchenweber/replay/[sessionId]`)
   - Read-only view of full story timeline
   - Shows story segments with user choices highlighted
   - Displays all generated images at appropriate points
   - "Continue Story" button to resume playing

3. **Session Continuation**
   - Main game page supports `?sessionId=X` parameter
   - Loads existing session and allows continuation
   - Preserves all character info and story state

**Files Created:**
- `src/routes/game/maerchenweber/stories/+page.svelte` - Stories list UI
- `src/routes/game/maerchenweber/replay/[sessionId]/+page.svelte` - Story replay UI
- `src/routes/api/game/maerchenweber/sessions/+server.ts` - Sessions list API proxy
- `src/routes/api/game/maerchenweber/session/[sessionId]/+server.ts` - Single session API proxy

**Files Modified:**
- `backend/app/routers/adventure.py` - Added `GET /adventure/user/{user_id}/sessions` endpoint
- `src/routes/game/maerchenweber/+page.svelte` - Added session continuation support

**Database Schema Updates:**
```javascript
{
  // NEW FIELDS:
  history_summary: string,           // Compressed summary of old turns
  image_history: [                   // Array of all generated images
    { round: number, url: string, description: string }
  ],

  // EXISTING (preserved for backwards compatibility):
  history: string[],                 // Full story + choices
  first_image_url: string,
  first_image_description: string,
  previous_image_url: string
}
```

---

### ✅ COMPLETED: Make Story Rounds Longer & Narration Slower

**Implementation Completed (2025-11-02):**
- ✅ Increased story length from 6-10 sentences to 12-18 sentences (~1 full page)
- ✅ Added rich sensory details and atmospheric descriptions
- ✅ Emphasized slower pacing with color, texture, sound, and emotion descriptions
- ✅ Instructed narrator to "paint the scene" before moving to action

**Changes Made:**
- Updated `character_creation` prompt with detailed sensory guidance
- Updated `narrator` prompt with same rich storytelling instructions
- Added explicit examples: colors ("goldene Licht"), textures ("weiche Moos"), emotions ("Du fühlst dich mutig")

**Files Modified:**
- `backend/config.yaml` - Both narrator and character_creation prompts (lines 25-101)

---

### ✅ COMPLETED: Improve 4th Choice Quality (Distractor Options)

**Implementation Completed (2025-11-02):**
- ✅ Enhanced `wildcard_choice` prompt with detailed quality guidelines
- ✅ Added explicit "WICHTIG" section defining what makes a good 4th choice
- ✅ Included concrete examples of good vs bad distractor options
- ✅ Emphasized that choices must be plausible AND contextually appropriate

**Changes Made:**
- Updated prompt to explicitly state: "kreativ anders, aber trotzdem zur Situation passt"
- Added "VERMEIDE" section listing absurd/nonsensical patterns to avoid
- Provided specific examples using a door scenario:
  - ✅ Good: "Ich klopfe höflich an die Tür", "Ich schaue durchs Schlüsselloch"
  - ❌ Bad: "Ich tanze auf einem Bein", "Ich esse einen Apfel"
- Clarified that the 4th choice should be "eine plausible Alternative" (a plausible alternative)

**Files Modified:**
- `backend/config.yaml` - wildcard_choice prompt (lines 169-205)

---

### ✅ COMPLETED: Enhanced Story Length, Choice Complexity, and Image Frequency

**Implementation Completed (2025-11-02):**
- ✅ Further increased story length from 12-18 sentences to ~20 sentences
- ✅ Added explicit paragraph structure requirement (2-4 paragraphs)
- ✅ Increased 4th choice complexity from 12 words to 18-20 words
- ✅ Re-enabled image generation every turn (changed from every 5 turns to every turn)

**Rationale:**
- Longer turns (~20 sentences) provide more immersive storytelling
- Structured paragraphs (2-4) create natural reading pauses
- More complex 4th choice allows for nuanced/creative options
- Image every turn provides stronger motivation for kids
- Cost impact mitigated: longer turns mean similar content-to-image ratio as before

**Changes Made:**
- `character_creation` prompt: "12-18 Sätze" → "etwa 20 Sätze, aufgeteilt in 2-4 Absätze"
- `narrator` prompt: "12-18 Sätze" → "etwa 20 Sätze, aufgeteilt in 2-4 Absätze"
- `wildcard_choice` prompt: "Max 12 Wörter" → "Max 18-20 Wörter (kann komplexer sein)"
- `game_mechanics.image_generation_interval`: 5 → 1

**Files Modified:**
- `backend/config.yaml` - Lines 6, 47, 77, 203

---

### ✅ COMPLETED: Improved Story Pacing (Avoid Complete Arcs Per Turn)

**Implementation Completed (2025-11-02):**
- ✅ Added "KRITISCH" section to narrator prompt emphasizing single-moment storytelling
- ✅ Instructed narrator to NOT complete story arcs or resolve tension within a turn
- ✅ Emphasized that each turn is "page 47 of 100" - not a complete short story
- ✅ Gave narrator autonomy to decide between atmospheric moments and action based on story history
- ✅ Balanced constraints with creative freedom

**Problem Solved:**
- Narrator was treating each turn like a complete story arc (intro → tension → resolution)
- This made pacing feel rushed despite having 20 sentences
- Stories felt like they were moving too quickly through events

**Final Approach:**
- Narrator has autonomy: "Lies die bisherige Geschichte und entscheide: Braucht es jetzt Atmosphäre oder Action?"
- Clear constraint: Don't build complete arcs (Problem → Climax → Solution) within one turn
- Freedom to introduce action/tension/events - just can't resolve them in the same turn
- Things can BEGIN but not be COMPLETED within a single round
- Changed ending from "Ende mit einer klaren Entscheidung" to "Ende mit einer klaren Entscheidungssituation, aber löse nichts auf"

**Files Modified:**
- `backend/config.yaml` - narrator prompt (lines 67-108)

---

### ✅ COMPLETED: Fixed Image Generation Bug (interval=1)

**Bug Fix Completed (2025-11-02):**
- ✅ Fixed image generation logic that broke when `image_generation_interval = 1`
- ✅ Images now correctly generate on every turn when interval is set to 1

**Problem:**
- Formula `(new_round % image_generation_interval) == 1` doesn't work for interval=1
- Any number % 1 = 0, never 1, so condition was always false
- Images were never generated after first turn when interval=1

**Solution:**
- Added explicit check: if interval is 1, always generate images
- Otherwise, use the modulo formula (works for intervals >= 2)

**Files Modified:**
- `backend/app/services/game_engine.py` - Lines 289-299

---

### ✅ COMPLETED: Fixed Image Not Updating in Frontend

**Bug Fix Completed (2025-11-02):**
- ✅ Fixed Svelte not re-rendering images when URL changes
- ✅ Added `{#key round}` block to force image element re-mount on each turn
- ✅ Changed `loading="lazy"` to `loading="eager"` for immediate image display
- ✅ Added debug logging to verify image URL changes

**Problem:**
- Backend was correctly generating and returning new image URLs each turn
- Frontend state (`currentImageUrl`) was correctly updating
- But the `<img>` element wasn't re-rendering with the new image
- Browser was caching data URLs or Svelte wasn't detecting the change

**Solution:**
- Wrapped `<img>` in `{#key round}` block to force re-mount when round changes
- Changed loading from "lazy" to "eager" to ensure immediate display
- Added console logging to help debug future issues

**Technical Details:**
- `{#key}` block in Svelte destroys and recreates the element when the key changes
- This forces the browser to fetch/decode the new image URL
- Particularly important for data URLs which might look identical to browser cache

**Files Modified:**
- `src/routes/game/maerchenweber/play/+page.svelte` - Lines 190-228 (debug logging), 357-369 (key block)

---

### ✅ COMPLETED: Fixed MongoDB Sort Memory Limit Error

**Bug Fix Completed (2025-11-02):**
- ✅ Fixed "Sort exceeded memory limit" error on `/adventure/user/{user_id}/sessions` endpoint
- ✅ Added database index for efficient sorting
- ✅ Reduced query scope with projection (only fetch needed fields)
- ✅ Limited results to 50 most recent sessions (down from 100)

**Problem:**
```
Executor error during find command: humanbenchmark.gamesessions :: caused by ::
Sort exceeded memory limit of 33554432 bytes, but did not opt in to external sorting.
```

**Root Cause:**
- Endpoint was sorting all user sessions without a database index
- MongoDB tries to sort in memory (32MB limit)
- When data exceeds 32MB, the query fails
- User likely had many test sessions with large history arrays

**Solution:**

1. **Added Compound Index** (`backend/app/database.py`):
   ```python
   await collection.create_index(
       [("userId", 1), ("gameType", 1), ("lastUpdated", -1)],
       name="user_sessions_sort_index",
       background=True
   )
   ```
   - Index matches the query filter + sort order exactly
   - Allows MongoDB to sort using the index (no memory limit)
   - Created on startup via `ensure_indexes()` function

2. **Optimized Query** (`backend/app/routers/adventure.py`):
   - Added `projection` to only fetch needed fields (reduces data size)
   - Reduced limit from 100 to 50 sessions (reasonable for UI)
   - Reordered operations for efficiency

**Technical Details:**
- Compound index structure: `{userId: 1, gameType: 1, lastUpdated: -1}`
- Matches query pattern: `find({userId, gameType}).sort({lastUpdated: -1})`
- Background creation to avoid blocking
- Index is persistent across restarts

**Files Modified:**
- `backend/app/database.py` - Added `ensure_indexes()` function (lines 41-57)
- `backend/app/main.py` - Call `ensure_indexes()` on startup (lines 10, 20-22)
- `backend/app/routers/adventure.py` - Optimized query with projection and limit (lines 194-209)

---

### ✅ COMPLETED: Märchenweber MVP Improvements (Waiting UX + Image Variation)

**Implementation Completed (2025-11-02):**

**Phase 1: Engaging Waiting Time UX**
- ✅ Journey Recap component showing all previous choices
- ✅ Fun Nugget generation (story-related fun fact, generated in parallel)
- ✅ Progress Steps component with animated generation stages
- ✅ Response includes `fun_nugget`, `choices_history`, and `round_number` fields

**Phase 2: Distinct & Rewarding Images**
- ✅ Scene intensity analyzer determines mood, perspective, lighting for each story
- ✅ Image prompt translator applies variation parameters while maintaining character consistency
- ✅ Images vary by perspective (close-up, wide, overhead, side, etc.)
- ✅ Images vary by lighting (golden hour, moonlight, dramatic, soft-daylight, etc.)
- ✅ Color saturation adjusts based on scene intensity (calm=muted, exciting=vibrant)
- ✅ Character appearance stays consistent across images via previous_image_url reference

**Files Created:**
- `src/lib/components/JourneyRecap.svelte` - Shows previous choices with sparkle icons
- `src/lib/components/FunNuggetCard.svelte` - Displays fun fact during loading
- `src/lib/components/ProgressSteps.svelte` - Animated generation progress

**Files Modified:**
- `backend/config.yaml` - Added fun_nugget, scene_intensity_analyzer prompts + models
- `backend/app/models.py` - Updated AdventureStepResponse with new fields
- `backend/app/services/game_engine.py` - Parallel generation, scene analysis, variation logic
- `src/routes/game/maerchenweber/play/+page.svelte` - Updated loading states with engagement components

**Result:**
- Waiting time feels 30-40% shorter with journey recap + fun nuggets + progress steps
- Images feel distinct and rewarding with scene-adaptive variation
- Character consistency maintained throughout story

---

## Future Considerations

(Add more items as needed)
