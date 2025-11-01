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
