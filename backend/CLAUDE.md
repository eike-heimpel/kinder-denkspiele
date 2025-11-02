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
- Unified choice generation (3 coherent choices)
- Wildcard injection for story creativity
- Content safety validation
- AI image generation with scene-adaptive variation
- Engaging waiting UX (journey recap, fun nuggets, progress steps)
- MongoDB persistence
- Full async/await with parallel generation

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
├── config.yaml              # Prompts, models, story wildcards, sampling params
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
Game Engine (Orchestration with parallel generation)
    ↓
Config Loader ← config.yaml
    ↓
LLM Service → OpenRouter API (parallel async calls)
    ├── Narrator (Gemini 2.5 Pro)
    ├── Fun Nugget Generator (Gemini 2.5 Flash)
    ├── Validator (Gemini 2.5 Flash)
    ├── Scene Analyzer (Gemini 2.5 Flash)
    ├── Image Translator (Gemini 2.5 Flash)
    ├── Image Generator (Gemini 2.5 Flash Image)
    └── Choice Agent Unified (Gemini 2.5 Flash)
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

### Turn Orchestration

See `game_engine.py` for implementation details. The orchestration includes:

**Parallel Generation:**
- Story + Fun Nugget generated simultaneously (no added wait time)

**Sequential Steps:**
- Load state → Update history → Narrator call (with story wildcard for variety)
- Safety validation → Choice generation (unified 3 choices)
- Scene analysis → Image translation → Image generation
- Save state → Return response with journey recap

**Image Variation:**
- Scene analyzer determines intensity, perspective, lighting
- Image translator applies variation parameters
- Character consistency maintained via previous image reference

**Waiting Time UX:**
- Journey recap (all previous choices)
- Fun nugget (story-relevant fun fact)
- Round number for progress tracking

### Anti-Repetition Strategy

See `config.yaml` for sampling parameters. Key mechanisms:

1. **Story Wildcard Injection** - Random story elements injected into narrator prompt (25+ options)
2. **High Temperature** - Creative, varied text generation
3. **Presence Penalty** - Discourages word repetition
4. **Unified Choice Generation** - 3 coherent yet diverse options per turn

---

## 📝 Configuration System

All prompts, models, and parameters configured in `config.yaml`. See the file for complete details.

### Key Components

**Models:** Narrator, Validator, Image Generator/Translator, Scene Analyzer, Fun Nugget Generator, Choice Agent (Unified)

**Prompts:** Character creation, narrator, validator, summarizer, fun nugget, scene analyzer, image translator, choice generation (Jinja2 templates)

**Game Mechanics:** Image generation interval, summarization interval, recent turns to keep

**Sampling Parameters:** Temperature, presence_penalty, top_p, max_tokens, reasoning settings per model

**Story Wildcards** (for narrator variety):
  - "Ein Tier in der Nähe beginnt plötzlich zu sprechen."
  - "Die Farbe des Himmels ändert sich abrupt zu einem sanften Lila."
  # ... 25+ total elements randomly injected into narrator prompt

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

All prompts support variable injection. See `config_loader.py` and `config.yaml` for examples.

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

**Response:** See `models.py` for schema. Includes:
- `session_id`
- `step` with `story_text`, `image_url`, `choices`, `fun_nugget`, `choices_history`, `round_number`
- Optional `timing` and `warnings` for debugging

### POST /adventure/turn

**Process a turn with user's choice**

**Request:** `session_id` and `choice_text`

**Response:** See `models.py`. Includes story, image, choices, fun nugget, journey recap, round number.

### GET /adventure/session/{session_id}

Returns session document from MongoDB. See `database.py` for schema.

---

## 🗄️ Database Schema

MongoDB collection `gamesessions` stores session state. See `game_engine.py` for schema details.

**Key fields:** userId, gameType, character details, history array (alternating stories and choices), round number, timestamps, image tracking (first_image_url, first_image_description, previous_image_url, image_history)

---

## 🤖 LLM Integration

See `llm_service.py` for implementation details. Uses OpenRouter API with async/await.

**Parallel generation:** Story + fun nugget use `asyncio.gather` to reduce wait time.

**Image generation:** Scene analysis → prompt translation with variation → image generation with character consistency.

---

## 🛡️ Content Safety

Validator LLM checks each story for age-appropriateness (7 years old). Unsafe content replaced with fallback text. See `_validate_safety()` in `game_engine.py`.

---

## 🎨 Prompt Engineering

All prompts in `config.yaml` use Jinja2 templating. Key principles:
- Age-specific language (7 years, second-grade reading level)
- DU-form (second person) for immersion
- Sensory details (colors, textures, sounds)
- Slow pacing with atmospheric descriptions
- JSON output mode for structured responses

See prompts in `config.yaml` for examples.

---

## 🔧 Development

**Running:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Environment:** Requires `MONGODB_URI` and `OPENROUTER_API_KEY` in root `.env`

**Dependencies:** See `pyproject.toml` - FastAPI, Motor (async MongoDB), httpx, Jinja2, PyYAML, Pydantic

---

## 📚 Related Documentation

- [Main CLAUDE.md](../CLAUDE.md) - Project overview
- [SvelteKit API Routes](../src/routes/api/CLAUDE.md) - Frontend proxy implementation
- [Game Page](../src/routes/game/maerchenweber/play/+page.svelte) - Frontend UI

---

**For implementation details, see code comments in `game_engine.py`, `llm_service.py`, and `config.yaml`.**
