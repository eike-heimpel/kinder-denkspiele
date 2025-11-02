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

### Make Story Rounds Longer & Narration Slower

**Problem:** Story rounds may feel too short, and narration speed might be too fast for kids to follow.

**Needed Changes:**
- Increase story length per round (more sentences/paragraphs)
- Slow down narration speed/pacing
- Possibly add pauses between sentences for comprehension
- Consider age-appropriate reading speeds

**Implementation:**
- Adjust prompt templates to request longer story segments
- Configure narration timing/animation in frontend
- Test with actual kids to find optimal pacing

---

### Improve 4th Choice Quality (Distractor Options)

**Problem:** The 4th choice option sometimes generates absurd or nonsensical alternatives that are too obviously wrong.

**Needed Changes:**
- Make distractor options more plausible and realistic
- Ensure all 4 choices are contextually appropriate
- Avoid completely absurd or out-of-place options
- Keep distractors challenging but believable

**Implementation:**
- Refine prompt instructions for generating the 4th choice
- Add examples of good vs. bad distractor options
- Consider validation rules for choice quality
- Test with kids to ensure choices are engaging but not confusing

---

## Future Considerations

(Add more items as needed)
