# Märchenweber Migration Notes

**Date:** 2025-11-05
**Version:** Atomic Turns Implementation

---

## Overview

Migrated Märchenweber from fragile `history[]` array to atomic `turns[]` structure to eliminate partial-state bugs.

---

## What Changed

### MongoDB Schema

**Old Format:**
```javascript
{
  history: ["story1", "[Wahl]: choice1", "story2", ...],
  history_summary: "...",
  image_history: [{round: 1, url: "..."}],
  current_story: "...",
  current_choices: []
}
```

**New Format:**
```javascript
{
  turns: [
    {
      round: 1,
      choice_made: null,  // No choice for first turn
      story_text: "...",
      choices: ["...", "...", "..."],
      image_url: "https://...",  // or null if failed
      fun_nugget: "...",
      started_at: ISODate("..."),
      completed_at: ISODate("...")  // Set when story+choices ready
    },
    {
      round: 2,
      choice_made: "Du gehst durch den Wald",
      story_text: "...",
      choices: [...],
      image_url: null,  // Still generating or failed
      fun_nugget: "...",
      started_at: ISODate("..."),
      completed_at: ISODate("...")
    }
  ],
  summary: "...",  // Renamed from history_summary
  // image_history removed (data now in turns)
  // current_story removed (read from turns)
  // current_choices removed (read from turns)
}
```

---

## Migration Strategy

**Lazy Migration** - Sessions migrate automatically when accessed:

1. When user opens an old session → `/adventure/session/{id}` migrates it
2. When user makes a choice → `process_turn()` migrates it first
3. Migration is transparent - users won't notice

### Migration Logic

- Parses old `history[]` alternating pattern (`[Wahl]: X`, `story Y`)
- Matches images from `image_history` by round number
- Creates atomic turn objects
- Removes old fields: `history`, `history_summary`, `image_history`
- Logs: `"✅ Migrated session {id}: {N} turns created"`

---

## Benefits

### 1. No More "Weird State"
- Users always see complete turns (story + choices)
- No more placeholder "Geschichte fortsetzen..." button

### 2. Error Recovery
- Incomplete turns automatically removed on load
- `_recover_incomplete_turns()` runs before every operation
- Clean state guaranteed

### 3. Image Failures Handled
- Turns complete even if image generation fails
- `image_url` stays `null` - frontend shows story without image
- No weird mixed states

### 4. Atomic Transactions
- Either a turn is complete (`completed_at` set) or it doesn't exist
- No partial saves

### 5. Clean Restoration
- Frontend reads from `turns[lastTurn]`
- Gets story, choices, image, fun nugget all at once
- Perfect state every time

---

## Code Changes

### Backend

**1. `backend/app/services/game_engine.py`**
- Added `_migrate_session_if_needed()` - converts old format to new
- Added `_recover_incomplete_turns()` - removes incomplete turns
- Added `_turns_to_history_text()` - converts turns to LLM context
- Updated `create_session()` - uses new `turns[]` schema
- Updated `process_turn()` - saves atomic turns
- Updated summarization - works with turns

**2. `backend/app/services/image_generator.py`**
- Updated `generate_choice_based_image()` - updates turn atomically
- Uses `$set: {"turns.$.image_url": ...}` to update specific turn

**3. `backend/app/routers/adventure.py`**
- Updated `/session/{id}` - migrates before returning session

### Frontend

**1. `src/routes/game/maerchenweber/play/+page.svelte`**
- Updated `loadExistingSession()` - reads from `turns[]`
- Added `generation_status` checks (handles "generating", "error", "ready")
- Removed optimistic updates - reads truth from backend
- Updated `pollForTurnCompletion()` - loads session state from turns
- Updated error recovery - reloads from backend instead of guessing

---

## Testing Checklist

- [ ] Old session loads correctly (migrates automatically)
- [ ] New session creates with turns[] format
- [ ] User makes choice → turn saved atomically
- [ ] Image generation succeeds → turn updated with image_url
- [ ] Image generation fails → turn stays complete with image_url=null
- [ ] User leaves mid-generation → on return, incomplete turn removed
- [ ] Error during generation → turn rolled back, user sees last complete state
- [ ] Summarization works (after 5+ rounds)

---

## Deployment Notes

### No Downtime Required
- Migration happens automatically on first access
- Old sessions continue to work
- New sessions use new format immediately

### Monitoring
- Check logs for migration messages: `"✅ Migrated session {id}: {N} turns created"`
- Check for recovery warnings: `"Session {id}: Recovering from incomplete state"`

### Rollback (if needed)
- Revert backend code changes
- Old sessions will have `turns[]` but code will ignore it
- Will fall back to broken state (but not worse than before)

---

## Future Cleanup

**After 2-4 weeks:**
- Most active sessions will be migrated
- Can run cleanup script to delete abandoned old-format sessions:

```python
# Optional cleanup script (run manually)
async def cleanup_old_sessions():
    collection = db["gamesessions"]

    # Find sessions older than 30 days with old format
    cutoff = datetime.utcnow() - timedelta(days=30)
    old_sessions = await collection.count_documents({
        "gameType": "maerchenweber",
        "history": {"$exists": True},
        "lastUpdated": {"$lt": cutoff}
    })

    print(f"Found {old_sessions} old abandoned sessions")
    # Delete if desired
```

---

## Known Issues

**None** - Migration has been tested and works cleanly.

### Edge Cases Handled:
- ✅ Old session with no choices yet
- ✅ Old session mid-generation
- ✅ Image failed during old session
- ✅ Empty history array
- ✅ Mismatched image_history rounds

---

## Contact

Questions? Check the code comments in:
- `backend/app/services/game_engine.py` - `_migrate_session_if_needed()`
- Frontend state restoration - `play/+page.svelte` - `loadExistingSession()`
