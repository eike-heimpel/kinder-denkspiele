---
title: "Märchenweber FastAPI Backend"
purpose: "LLM-powered storytelling game backend for kids"
parent: "../CLAUDE.md"
last_updated: "2025-11-01"
keywords: ["fastapi", "python", "llm", "openrouter", "storytelling", "mongodb", "async"]
---

# 🎭 Märchenweber Backend - FastAPI

**Layer:** Backend API (Python/FastAPI)
**Location:** `backend/`
**Parent Guide:** [Main CLAUDE.md](../CLAUDE.md)

---

## 🎯 Purpose

FastAPI backend for the Märchenweber ("Story Weaver") game - a dynamic LLM-powered storytelling experience for 7-year-old children. The system generates unique, safe, non-repetitive German fairy tales through advanced AI orchestration.

**Key Features:**
- LLM-powered story generation (German language)
- "Council of Choices" - 3 different models for diverse options
- Wildcard injection for creativity
- Content safety validation
- AI image generation
- MongoDB persistence
- Full async/await

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with CORS
│   ├── config.py            # Environment variables
│   ├── models.py            # Pydantic request/response models
│   ├── database.py          # Motor MongoDB connection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── config_loader.py # YAML + Jinja2 loader
│   │   ├── llm_service.py   # OpenRouter API client
│   │   └── game_engine.py   # Core orchestration logic
│   └── routers/
│       ├── __init__.py
│       └── adventure.py     # /adventure/start & /adventure/turn
├── config.yaml              # Prompts, models, wildcards, sampling params
├── pyproject.toml           # uv dependencies
├── .python-version          # Python 3.12
└── CLAUDE.md                # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ (managed by uv)
- MongoDB Atlas connection (shared with SvelteKit)
- OpenRouter API key

### Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### Environment Variables

Add to root `.env` file (shared with SvelteKit):

```bash
MONGODB_URI=mongodb+srv://...  # Existing MongoDB Atlas connection
OPENROUTER_API_KEY=sk-or-v1-...  # Your OpenRouter API key
```

### Running the Server

```bash
# Development with auto-reload
uv run uvicorn app.main:app --reload --port 8000

# Production
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`

---

## 🏗️ Architecture

### System Overview

```
SvelteKit Frontend (Port 5173)
    ↓ (proxy requests)
FastAPI Backend (Port 8000)
    ↓
Game Engine (Orchestration)
    ↓
Config Loader ← config.yaml
    ↓
LLM Service → OpenRouter API
    ├── Narrator Model (Gemini 2.0 Flash)
    ├── Validator Model (Gemini 1.5 Flash)
    ├── Image Generator (Gemini 2.0 Flash)
    ├── Choice Agent Brave (Claude 3.5 Sonnet)
    ├── Choice Agent Silly (Gemini 2.0 Flash)
    └── Choice Agent Careful (GPT-4o Mini)
    ↓
MongoDB (Shared)
```

### Integration with SvelteKit

The FastAPI backend runs **alongside** SvelteKit, not replacing it:

```
Frontend Request → SvelteKit Proxy → FastAPI Backend → MongoDB
                   (/api/game/maerchenweber/*)
```

**Proxy endpoints (in SvelteKit):**
- `src/routes/api/game/maerchenweber/start/+server.ts`
- `src/routes/api/game/maerchenweber/turn/+server.ts`

**CORS:** Configured to allow `localhost:5173` (SvelteKit dev server)

---

## 🎮 Core Game Logic

### Turn Orchestration Chain

The `game_engine.py` implements this exact sequence on every turn:

1. **Load State** - Fetch GameSession from MongoDB
2. **Update History** - Append user's choice
3. **Wildcard Selection** - Random element injection
4. **Narrator Call** - Generate story with wildcard
5. **Safety Validation** - Check age-appropriateness
6. **Council of Choices** - 3 parallel LLM calls (brave/silly/careful)
7. **Image Generation** - Translate to English → Generate image
8. **Save State** - Persist to MongoDB
9. **Return Response** - Send to client

### Anti-Repetition Strategy

**Critical for non-repetitive stories:**

1. **Wildcard Injection**: Every turn includes a random element from 25+ options
2. **Council of Choices**: 3 different models with different personalities
3. **Sampling Parameters**:
   - `temperature: 0.95` (high creativity)
   - `presence_penalty: 0.4` (discourage repetition)
   - `top_p: 0.95` (diverse token selection)
4. **Different Models**: Variety through model diversity

---

## 📝 Configuration System

### config.yaml Structure

```yaml
models:
  narrator: "google/gemini-2.5-pro"
  validator: "google/gemini-2.5-flash"
  image_generator: "openai/gpt-5-image-mini"
  image_translator: "google/gemini-flash-1.5"
  choice_agent_brave: "qwen/qwen3-next-80b-a3b-instruct"
  choice_agent_silly: "google/gemini-2.5-flash"
  choice_agent_careful: "openai/gpt-5-mini"

prompts:
  character_creation: "..." # Jinja2 template
  narrator: "..."           # {{ history }}, {{ wildcard }}
  validator: "..."          # {{ german_text }}
  image_prompt_translator: "..." # {{ german_image_prompt }}
  choice_prompts:
    brave: "..."
    silly: "..."
    careful: "..."

wildcards:
  - "Ein Tier in der Nähe beginnt plötzlich zu sprechen."
  - "Die Farbe des Himmels ändert sich abrupt zu einem sanften Lila."
  # ... 25+ total

sampling_params:
  narrator:
    temperature: 0.95
    presence_penalty: 0.4
    top_p: 0.95
    max_tokens: 500
    reasoning:
      max_tokens: 2000  # Gemini uses max_tokens for reasoning

  choice_agent_brave:
    temperature: 1.1
    reasoning:
      max_tokens: 1000  # Qwen: moderate reasoning

  choice_agent_careful:
    temperature: 0.8
    reasoning:
      effort: "medium"  # OpenAI uses effort levels (high/medium/low)
  # ... params for each agent
```

**Reasoning Configuration:**
- **Gemini models**: Use `reasoning.max_tokens` (integer)
- **OpenAI models**: Use `reasoning.effort` ("high", "medium", "low")
- **Other models**: Check model documentation (most support max_tokens)
- Reasoning tokens allow models to "think" before responding
- Higher values = more thoughtful responses but higher cost

### Jinja2 Templating

All prompts support variable injection:

```python
from app.services.config_loader import get_config_loader

config = get_config_loader()
prompt = config.get_prompt(
    "narrator",
    history="Previous story...",
    wildcard="Ein Vogel beginnt zu singen."
)
```

---

## 🔌 API Endpoints

### POST /adventure/start

**Start a new adventure**

**Request:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "character_name": "Prinzessin Luna",
  "character_description": "eine mutige Prinzessin",
  "story_theme": "ein verzauberter Wald"
}
```

**Response:**
```json
{
  "session_id": "673abc123def456789012345",
  "step": {
    "story_text": "Es war einmal...",
    "image_url": "data:image/png;base64,...",
    "choices": [
      "Ich gehe mutig in den Wald hinein",
      "Ich tanze im Mondlicht",
      "Ich schaue mich vorsichtig um"
    ]
  }
}
```

### POST /adventure/turn

**Process a turn with user's choice**

**Request:**
```json
{
  "session_id": "673abc123def456789012345",
  "choice_text": "Ich gehe mutig in den Wald hinein"
}
```

**Response:**
```json
{
  "story_text": "Als Luna mutig...",
  "image_url": "data:image/png;base64,...",
  "choices": [
    "Ich spreche mit dem Tier",
    "Ich lache fröhlich",
    "Ich bleibe ruhig stehen"
  ]
}
```

### GET /adventure/session/{session_id}

**Get current session state (for debugging)**

**Response:**
```json
{
  "_id": "673abc123def456789012345",
  "userId": "507f1f77bcf86cd799439011",
  "gameType": "maerchenweber",
  "character_name": "Prinzessin Luna",
  "history": ["Story 1", "[Wahl]: Choice 1", "Story 2", ...],
  "round": 5,
  "createdAt": "2025-11-01T12:00:00Z",
  "lastUpdated": "2025-11-01T12:05:00Z"
}
```

---

## 🗄️ Database Schema

### MongoDB Collection: `gamesessions`

```javascript
{
  _id: ObjectId,
  userId: "507f1f77bcf86cd799439011",
  gameType: "maerchenweber",
  character_name: "Prinzessin Luna",
  character_description: "eine mutige Prinzessin",
  story_theme: "ein verzauberter Wald",
  reading_level: "second_grade",
  history: [
    "Es war einmal...",                    // Story 1
    "[Wahl]: Ich gehe in den Wald",       // User choice
    "Luna ging in den Wald...",           // Story 2
    "[Wahl]: Ich spreche mit dem Vogel",  // User choice
    // ... continues
  ],
  score: 0,
  round: 3,
  createdAt: ISODate("2025-11-01T12:00:00Z"),
  lastUpdated: ISODate("2025-11-01T12:05:00Z")
}
```

**Note:** Shares the same `gamesessions` collection as other games in the project.

---

## 🤖 LLM Integration

### OpenRouter API

**Base URL:** `https://openrouter.ai/api/v1/chat/completions`

**Headers:**
```python
{
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost:5173",
    "X-Title": "Märchenweber"
}
```

### Text Generation

```python
from app.services.llm_service import get_llm_service

llm = get_llm_service()
response = await llm.generate_text(
    prompt="Tell a story...",
    model="google/gemini-2.0-flash-exp:free",
    sampling_params={
        "temperature": 0.95,
        "presence_penalty": 0.4,
        "top_p": 0.95
    },
    json_mode=True  # Request JSON response
)
```

### Image Generation

```python
image_url = await llm.generate_image(
    prompt="A magical forest, digital art, vibrant colors, whimsical fairy tale style",
    model="google/gemini-2.0-flash-exp:free",
    aspect_ratio="4:3"
)
# Returns: Base64 data URL or hosted URL
```

### Council of Choices (Parallel)

```python
import asyncio

brave_task = llm.generate_text(brave_prompt, brave_model, brave_params)
silly_task = llm.generate_text(silly_prompt, silly_model, silly_params)
careful_task = llm.generate_text(careful_prompt, careful_model, careful_params)

choices = await asyncio.gather(brave_task, silly_task, careful_task)
```

---

## 🛡️ Content Safety

### Validation Flow

1. **Narrator generates story** → `story_text`
2. **Validator checks safety**:
   ```python
   prompt = "Is the following text appropriate for a 7-year-old? SAFE or UNSAFE: {text}"
   response = await llm.generate_text(prompt, validator_model)
   is_safe = "SAFE" in response.upper()
   ```
3. **If UNSAFE**:
   - Log incident
   - Replace with fallback: `"Oh, lass uns eine andere Geschichte beginnen!"`
   - Do NOT show to child

### Safety Criteria

- No scary/violent themes
- No inappropriate content
- Age-appropriate language (7 years old)
- Whimsical fairy tale style only

---

## 🎨 Prompt Engineering

### Best Practices

1. **Be specific about age**: "für ein 7-jähriges Kind"
2. **Reinforce style**: "märchenhaft", "fantasievoll", "magisch"
3. **Use Jinja2 variables**: `{{ character_name }}`, `{{ wildcard }}`
4. **Request JSON format**: Explicitly ask for structured output
5. **Inject wildcards**: Always include a random element

### Example Narrator Prompt

```jinja2
Du bist ein kreativer Geschichtenerzähler für Kinder.

Bisherige Geschichte:
{{ history }}

WICHTIG: Baue das folgende Element ein:
"{{ wildcard }}"

Setze die Geschichte fort mit:
- 3-4 Sätzen in deutscher Sprache
- Märchenhafter Sprache
- Altersgerecht für 7-jährige

Antworte mit JSON:
{
  "story_text": "...",
  "image_prompt": "..."
}
```

---

## 🔧 Development Tips

### Testing Locally

```bash
# Terminal 1: MongoDB (already running via Docker)
# Terminal 2: SvelteKit
npm run dev

# Terminal 3: FastAPI
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### Testing API Directly

```bash
# Health check
curl http://localhost:8000/health

# Start adventure
curl -X POST http://localhost:8000/adventure/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "character_name": "Luna",
    "character_description": "eine mutige Prinzessin",
    "story_theme": "ein verzauberter Wald"
  }'
```

### Debugging

```python
# Add logging
import logging
logger = logging.getLogger(__name__)

logger.info(f"Generated story: {story_text[:100]}")
logger.warning(f"Unsafe content detected")
logger.error(f"API call failed: {error}")
```

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'app'`
**Solution:** Run from backend directory: `cd backend && uv run uvicorn ...`

**Issue:** `MONGODB_URI is not set`
**Solution:** Ensure root `.env` has `MONGODB_URI` variable

**Issue:** `OPENROUTER_API_KEY is not set`
**Solution:** Add `OPENROUTER_API_KEY=sk-or-v1-...` to root `.env`

**Issue:** `Connection refused to localhost:8000`
**Solution:** Start FastAPI server first

---

## 📦 Dependencies

### Core (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi>=0.120.4",      # Modern web framework
    "uvicorn>=0.38.0",       # ASGI server
    "motor>=3.7.1",          # Async MongoDB driver
    "jinja2>=3.1.6",         # Template engine
    "pyyaml>=6.0.3",         # YAML parser
    "httpx>=0.28.1",         # Async HTTP client
    "python-dotenv>=1.2.1",  # Environment variables
    "pydantic>=2.12.3",      # Data validation
    "pydantic-settings>=2.11.0"  # Settings management
]
```

### Why These Models?

- **Gemini 2.5 Pro/Flash**: Advanced reasoning, excellent German support
- **Qwen 3 Next 80B**: High-quality reasoning for creative choices
- **GPT-5 Mini**: Latest OpenAI model with effort-based reasoning
- **Mix of providers**: Diversity prevents repetition
- **Reasoning-capable**: All models support extended thinking for better responses

---

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secrets manager
2. **CORS**: Update allowed origins for production domain
3. **Rate Limiting**: Add to prevent abuse
4. **Logging**: Configure proper log aggregation
5. **Monitoring**: Track LLM costs and latency
6. **Caching**: Consider caching config.yaml
7. **Error Handling**: Graceful degradation if LLM fails

### Docker (Optional)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy app
COPY . .

# Run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 Cost Estimation

### Per Story Turn

- Narrator: ~500 tokens × $0.01/1M = $0.000005
- Validator: ~50 tokens × $0.01/1M = $0.0000005
- 3 Choice Agents: ~150 tokens × $0.02/1M = $0.000003
- Image: ~1 image × $0.02 = $0.02
- **Total per turn: ~$0.02**

### Per Session (10 turns)

- **~$0.20 per child per adventure**
- Very affordable for a unique storytelling experience

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Start adventure
curl -X POST http://localhost:8000/adventure/start -H "Content-Type: application/json" -d '{"user_id":"test","character_name":"Luna","character_description":"eine Prinzessin","story_theme":"ein Wald"}'

# 2. Get session ID from response
SESSION_ID="..."

# 3. Make a choice
curl -X POST http://localhost:8000/adventure/turn -H "Content-Type: application/json" -d '{"session_id":"'$SESSION_ID'","choice_text":"Ich gehe vorwärts"}'

# 4. Check session
curl http://localhost:8000/adventure/session/$SESSION_ID
```

### Unit Testing (Future)

```python
# tests/test_game_engine.py
import pytest
from app.services.game_engine import GameEngine

@pytest.mark.asyncio
async def test_start_adventure():
    engine = GameEngine()
    result = await engine.start_adventure(
        user_id="test",
        character_name="Luna",
        character_description="eine Prinzessin",
        story_theme="ein Wald"
    )
    assert "session_id" in result
    assert "step" in result
```

---

## 📚 Related Documentation

- [Main CLAUDE.md](../CLAUDE.md) - Project overview
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture
- [API-REFERENCE.md](../docs/API-REFERENCE.md) - API documentation
- [SvelteKit API Routes](../src/routes/api/CLAUDE.md) - Proxy implementation
- [Game Page](../src/routes/game/maerchenweber/+page.svelte) - Frontend UI

---

## 🎯 Key Takeaways

1. **Parallel Architecture**: FastAPI runs alongside SvelteKit (not replacing)
2. **YAML Config**: All prompts/models externalized for easy tweaking
3. **Council of Choices**: 3 models = diversity
4. **Wildcards**: Random injection prevents repetition
5. **Safety First**: Always validate before showing to child
6. **Async Everything**: Motor + httpx for performance
7. **Shared MongoDB**: Uses existing Atlas connection
8. **German Language**: All stories and choices in German
9. **Age 7 Target**: Designed for second-grade reading level
10. **Cost Effective**: ~$0.02 per turn with mostly free models

---

**For questions about implementation details, check the inline code comments in `game_engine.py` - the core orchestration logic is extensively documented.**
