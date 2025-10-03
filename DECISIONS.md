# 📋 Technical Decisions Log

**Purpose:** Document WHY we made specific technical choices for AI agents to understand context.  
**Related Docs:** [AI-GUIDE.md](./AI-GUIDE.md) | [ARCHITECTURE.md](./ARCHITECTURE.md) | [TECH-STACK.md](./TECH-STACK.md)

---

## Architecture Decisions

### Layered Architecture Pattern

**Decision:** Use strict layer separation (UI → API → Service → Repository → DB)

**Why:**
- **Maintainability:** Each layer has a single responsibility
- **Testability:** Layers can be tested in isolation
- **Extensibility:** Easy to add new games or features
- **Clarity:** Clear data flow, easier for AI agents to understand

**Trade-offs:**
- More files and boilerplate
- Slightly more complex for simple operations
- **Worth it:** The complexity is minimal for the benefits gained

**Alternative Considered:** Direct database access from API routes
- **Rejected:** Would make it hard to add caching, validation, or swap databases

---

### Repository Pattern

**Decision:** Abstract all database operations into repository classes

**Why:**
- **Database Agnostic:** Could swap MongoDB for PostgreSQL without changing services
- **Consistent API:** All data access follows same pattern
- **Testable:** Easy to mock for testing
- **Type Safety:** TypeScript interfaces ensure correct data handling

**Trade-offs:**
- Extra layer of abstraction
- More code than direct queries
- **Worth it:** Flexibility for future changes

**Example:**
```typescript
// Repository handles all MongoDB specifics
class UserRepository {
    async findById(id: string): Promise<User | null>
}

// Service just uses the interface
class GameEngine {
    async startGame(userId: string) {
        const user = await userRepo.findById(userId);
    }
}
```

---

### Service Layer for Game Logic

**Decision:** Separate game logic into service classes (GameEngine, WordService)

**Why:**
- **Reusable:** Same logic for API and potential CLI tools
- **Testable:** Can test game rules without HTTP or database
- **Clear Ownership:** Game rules live in one place
- **Stateful Operations:** GameEngine maintains game state

**Trade-offs:**
- More classes to understand
- **Worth it:** Makes game logic portable and testable

---

## Technology Choices

### SvelteKit + Svelte 5

**Decision:** Use SvelteKit with Svelte 5 (latest)

**Why:**
- **Modern:** Svelte 5 runes are more intuitive than Svelte 4
- **Performance:** Fine-grained reactivity, smaller bundles
- **Full-stack:** API routes + UI in one framework
- **Developer Experience:** Hot reload, TypeScript support, file-based routing
- **Kid-Friendly:** Fast rendering for responsive UI

**Trade-offs:**
- Svelte 5 is relatively new (released 2024)
- Less Stack Overflow answers than React
- **Worth it:** Better performance, cleaner code

**Alternative Considered:** Next.js + React
- **Rejected:** React is more verbose, larger bundles, slower

---

### Tailwind CSS v4

**Decision:** Use Tailwind CSS v4 for styling

**Why:**
- **Rapid Development:** No need to write custom CSS
- **Consistency:** Design system built-in
- **Kid-Friendly:** Easy to make colorful, large UI elements
- **JIT Compilation:** Only generates used classes
- **No Configuration:** v4 works without config file

**Trade-offs:**
- Learning curve for Tailwind
- HTML can get verbose with many classes
- **Worth it:** Faster development, consistent design

**Alternative Considered:** CSS Modules or plain CSS
- **Rejected:** More work to maintain, inconsistent patterns

---

### MongoDB (NoSQL)

**Decision:** Use MongoDB instead of PostgreSQL or SQLite

**Why:**
- **Flexible Schema:** Easy to add fields without migrations
- **JSON-Like Data:** Natural fit for JavaScript/TypeScript
- **Document Model:** Game sessions naturally fit document structure
- **Docker Setup:** Easy to run locally
- **Embedded Arrays:** Can store `seenWords` and `wordsShown` as arrays

**Trade-offs:**
- No enforced schema (must validate in code)
- No joins (but we don't need them)
- **Worth it:** Simpler setup, flexible for MVP

**Alternative Considered:** PostgreSQL
- **Rejected:** Overkill for this project, requires migrations

---

### Docker for MongoDB

**Decision:** Run MongoDB in Docker container

**Why:**
- **No Installation:** Don't need to install MongoDB globally
- **Consistent Environment:** Same setup across machines
- **Easy Start/Stop:** `docker-compose up/down`
- **Isolated:** Doesn't interfere with system

**Trade-offs:**
- Requires Docker installed
- **Worth it:** Cleaner development environment

---

## Design Patterns

### Singleton Pattern for Database Connection

**Decision:** Use singleton pattern for MongoDB client

**Why:**
- **Connection Pooling:** Reuse connections, don't create new ones
- **Performance:** Connecting to DB is expensive
- **MongoDB Driver Requirement:** Driver handles pooling internally

**Code:**
```typescript
let client: MongoClient | null = null;
let db: Db | null = null;

export async function connectToDatabase(): Promise<Db> {
    if (db) return db;  // Reuse existing
    // ... create new connection
}
```

**Alternative Considered:** Create new connection per request
- **Rejected:** Would exhaust connection pool, slow performance

---

### Type-First Development

**Decision:** Define all types in `src/lib/types/index.ts` first

**Why:**
- **Single Source of Truth:** All types in one place
- **Type Safety:** Catch errors at compile time
- **Documentation:** Types document the data structure
- **Refactoring:** TypeScript helps find all usages

**Example:**
```typescript
// Define once
export interface GameSession { ... }

// Use everywhere
const session: GameSession = { ... }
```

**Alternative Considered:** Inline types
- **Rejected:** Duplication, inconsistency

---

## Feature Decisions

### No Authentication (Yet)

**Decision:** No user authentication in MVP

**Why:**
- **Local Deployment:** Runs on home server, trusted environment
- **Simplicity:** Faster development, no complexity
- **Kid-Friendly:** Kids just click their name, no password
- **MVP:** Can add auth later for production

**Trade-offs:**
- Anyone with access can play as anyone
- **Acceptable:** For local use only

**Future:** Add authentication before public deployment

---

### Simple User Management

**Decision:** Users identified by name only, no email/password

**Why:**
- **Kids-First:** 5-8 year olds can't manage passwords
- **Local Use:** No security concerns
- **Quick Access:** Click name and play
- **MVP:** Minimal viable feature

**Alternative Considered:** Family accounts with sub-users
- **Rejected:** Too complex for MVP

---

### Two Difficulty Levels Only

**Decision:** Easy and Hard, no Medium

**Why:**
- **Simple Choice:** Kids can understand two options
- **Clear Distinction:** Easy = 5-6 years, Hard = 7-8 years
- **Word Pools:** 145 words divided into two clear categories
- **UI Clarity:** Two big buttons, easy to choose

**Alternative Considered:** Three or more levels
- **Rejected:** Too many choices, harder to balance

---

### German-Only Interface

**Decision:** All text and words in German

**Why:**
- **Target Audience:** German-speaking kids
- **Language Practice:** Help kids learn German
- **Simplicity:** No i18n complexity in MVP

**Future:** Could add multi-language support later

---

### Lives System (3 Lives)

**Decision:** Game ends after 3 mistakes

**Why:**
- **Kid-Friendly:** Forgiving enough to learn
- **Quick Games:** Kids won't get bored
- **Balancing:** Tested with target age group
- **Visual:** Hearts are clear indicator

**Alternative Considered:** Unlimited lives, time limit
- **Rejected:** Kids might play forever or feel rushed

---

## UI/UX Decisions

### Large Buttons with Emojis

**Decision:** All interactive elements are large with emoji icons

**Why:**
- **Kid-Friendly:** Easy for small hands to tap
- **Visual:** Emojis add color and meaning
- **Accessibility:** Large targets reduce mistakes
- **Fun:** Engaging for children

**Sizes:**
- Small buttons: `text-base` (16px) + `px-6 py-3`
- Large buttons: `text-3xl` (30px) + `px-14 py-7`

---

### Gradient Backgrounds

**Decision:** Use animated gradient backgrounds everywhere

**Why:**
- **Visual Interest:** More engaging than solid colors
- **Kid-Friendly:** Colorful and playful
- **Modern:** Fits current design trends
- **Subtle Animation:** Keeps attention without distracting

**Alternative Considered:** Solid colors
- **Rejected:** Too plain, less engaging

---

### No Timers in MVP

**Decision:** No time pressure in current version

**Why:**
- **Kid-Friendly:** Reduces stress
- **Focus on Learning:** Let kids think
- **MVP:** Add timer as optional feature later

**Future:** Could add timer for advanced mode

---

### Score-Only Tracking

**Decision:** Track score and lives, not time or accuracy %

**Why:**
- **Simple:** Easy for kids to understand
- **Motivating:** Higher score = better
- **MVP:** Can add more metrics later

**Future:** Add accuracy %, average time per word, streaks

---

## Code Style Decisions

### Svelte 5 Runes Over Stores

**Decision:** Use `$state()` and `$derived()` instead of Svelte stores

**Why:**
- **Simpler:** Runes are built-in, no imports
- **Local State:** Most state is component-local
- **Performance:** Runes have fine-grained reactivity
- **Modern:** This is the Svelte 5 way

**When to Use Stores:**
- Global app state (not needed yet)
- Shared across many components (not needed yet)

---

### Inline Styles with Tailwind

**Decision:** Use Tailwind classes directly in components, not separate CSS files

**Why:**
- **Colocation:** Styles next to markup
- **Clarity:** See exactly what styles apply
- **No Naming:** Don't need to think of class names
- **JIT:** Only generates used classes

**Trade-offs:**
- Long class strings in HTML
- **Worth it:** Faster development, no CSS file maintenance

---

### TypeScript Strict Mode

**Decision:** Enable TypeScript strict mode

**Why:**
- **Type Safety:** Catch more errors at compile time
- **Better DX:** Better autocomplete and hints
- **Fewer Bugs:** Enforces null checks, type assertions

**Trade-offs:**
- More explicit type annotations needed
- **Worth it:** Fewer runtime errors

---

### Error Handling Strategy

**Decision:** Throw errors in repositories, handle in API routes

**Why:**
- **Clear Errors:** Specific error messages
- **HTTP Status Codes:** Map to proper status codes in API
- **Logging:** Can log at API layer
- **User Feedback:** Return friendly messages

**Example:**
```typescript
// Repository
if (!user) {
    throw new Error('User not found');
}

// API
try {
    const user = await repo.findById(id);
    return json(user);
} catch (error) {
    return json({ error: error.message }, { status: 404 });
}
```

---

## Testing Decisions

### Unit Tests for Critical Logic

**Decision:** Add unit tests for GameEngine and WordService

**Why:**
- **Critical Logic:** These services contain core game mechanics
- **Easy to Test:** No database or HTTP dependencies needed
- **Fast Feedback:** Tests run in milliseconds
- **Bug Prevention:** Caught duplicate word bug with tests
- **Confidence:** Can refactor knowing tests will catch regressions

**What We Test:**
1. ✅ GameEngine business logic (12 tests)
   - Game state management
   - Score/lives calculations
   - Word tracking
   - Game over conditions
   - No consecutive duplicates
2. ✅ WordService selection logic (20 tests)
   - Word pool initialization
   - Random selection with exclusions
   - Seen word handling
   - Edge cases (empty pools, all excluded)
   - Randomness validation

**What We Don't Test (Yet):**
- ❌ API endpoints (would need database setup)
- ❌ Repository layer (requires MongoDB)
- ❌ E2E flows (would need Playwright)
- ❌ Svelte components (would need component testing setup)

**Future:** Add integration and E2E tests before production deployment

---

## Deployment Decisions

### Local-Only Deployment

**Decision:** Designed to run on local server only

**Why:**
- **User Requirement:** For home use
- **No Auth Needed:** Trusted environment
- **Simplicity:** No cloud complexity
- **Cost:** Free

**Future:** If public deployment:
- Add authentication
- Use cloud MongoDB (Atlas)
- Add rate limiting
- Enable HTTPS
- Add monitoring

---

## Performance Decisions

### No Caching in MVP

**Decision:** No Redis or in-memory caching

**Why:**
- **Small Scale:** Few users, local deployment
- **MongoDB Fast Enough:** Queries are simple
- **MVP:** Premature optimization

**Future:** Add caching if performance issues

---

### No CDN

**Decision:** Serve static assets directly from Vite

**Why:**
- **Local Deployment:** No need for CDN
- **Small Assets:** Few images, minimal CSS/JS
- **Development:** Easier to debug

**Future:** Use CDN for public deployment

---

## Future Considerations

### What We Might Add

1. **More Games:** Reaction time, number memory, typing speed
2. **User Profiles:** Avatars, preferences, achievements
3. **Leaderboards:** Compare scores with family
4. **Sound Effects:** Audio feedback for actions
5. **Animations:** More engaging transitions
6. **Statistics:** Detailed progress tracking
7. **Multi-language:** Support for other languages
8. **Mobile App:** Native mobile version
9. **Offline Mode:** PWA functionality
10. **Social Features:** Share scores, challenges

### What We Won't Add

1. **Monetization:** This is a family project, not commercial
2. **Ads:** Keep it clean for kids
3. **Social Login:** No need for OAuth
4. **Complex Analytics:** Keep it simple

---

## Lessons Learned

### What Worked Well

1. **Layered Architecture:** Easy to add new games
2. **TypeScript:** Caught many errors early
3. **Svelte 5:** Cleaner code than Svelte 4
4. **Tailwind v4:** Fast styling without config
5. **Docker:** Easy MongoDB setup

### What Could Improve

1. **Documentation First:** Write this earlier
2. **Type Definitions:** Define types before coding
3. **API Design:** Plan endpoints before implementing
4. **Testing:** Should have added basic tests

---

## Questions for Future AI Agents

**Q: Why MongoDB instead of PostgreSQL?**  
A: Flexible schema, natural JSON storage, easier setup. We don't need relational features.

**Q: Why no authentication?**  
A: Local deployment only. Add auth before public deployment.

**Q: Why Svelte instead of React?**  
A: Smaller bundles, faster rendering, cleaner syntax. Better for kid-focused app.

**Q: Why no tests?**  
A: MVP focus. Add tests before scaling or public deployment.

**Q: Why Tailwind classes inline?**  
A: Faster development, better colocation. Worth the verbose HTML.

**Q: Why only 3 lives?**  
A: Balanced for target age (5-8 years). Forgiving but not unlimited.

---

**Related Documentation:**
- [AI-GUIDE.md](./AI-GUIDE.md) - Overall guide for AI agents
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design details
- [TECH-STACK.md](./TECH-STACK.md) - Technology specifications
