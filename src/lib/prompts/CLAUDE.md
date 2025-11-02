---
title: "LLM Prompt Templates"
purpose: "YAML + Jinja2 prompt templates for LLM-powered features"
parent: "../../../CLAUDE.md"
last_updated: "2025-11-02"
keywords: ["llm", "prompts", "yaml", "jinja2", "templates", "logic-lab"]
---

# 🎨 Prompts - LLM Prompt Templates

**Layer:** Data/Configuration
**Location:** `src/lib/prompts/`
**Parent Guide:** [Main CLAUDE.md](../../../CLAUDE.md)

---

## 🎯 Purpose

This directory contains **YAML-based prompt templates** for LLM-powered features. Prompts are separated from code using YAML + Jinja2 templating for easy iteration without code changes.

**Currently used by:** Logic Lab game

---

## 📂 Files

```
src/lib/prompts/
├── generate-problem.yaml      # Main problem generation prompt
└── validate-problem.yaml      # Problem validation prompt
```

---

## 📝 File Format

Each YAML file contains:

```yaml
version: "1.0.0"
model: "google/gemini-2.5-flash"
temperature: 0.9
max_tokens: 1000
response_format:
  type: "json_object"

system_prompt: |
  Du bist ein kreativer Lehrer...
  {{ variable_here }}

user_prompt: |
  Erstelle ein neues {{ problem_type }}.

  {% if performance_history|length > 0 %}
  BISHERIGE PERFORMANCE:
  {% for item in performance_history %}
  - "{{ item.question }}" → {{ "✓" if item.correct else "✗" }}
  {% endfor %}
  {% endif %}
```

### Structure

- **version:** Template version (semantic versioning)
- **model:** OpenRouter model ID (e.g., `google/gemini-2.5-flash`)
- **temperature:** Creativity level (0.0 = deterministic, 2.0 = very creative)
- **max_tokens:** Maximum response length
- **response_format:** Expected response type (typically `json_object`)
- **system_prompt:** System-level instructions (with Jinja2 variables)
- **user_prompt:** User-facing prompt (with Jinja2 variables and control flow)

---

## 🔧 How It Works

### 1. PromptLoader Service

**File:** `src/lib/services/prompt-loader.service.ts`

Loads YAML files and renders Jinja2 templates:

```typescript
import { PromptLoader } from '$lib/services/prompt-loader.service';

const loader = new PromptLoader();
const rendered = loader.renderPrompt('generate-problem', {
  age: 7,
  difficulty: 'easy',
  problem_type: 'pattern',
  performance_history: [...]
});

// Returns:
// {
//   model: 'google/gemini-2.5-flash',
//   temperature: 0.9,
//   max_tokens: 1000,
//   system_prompt: '...',  // with variables filled
//   user_prompt: '...'      // with variables filled
// }
```

### 2. LLMService Usage

**File:** `src/lib/services/llm.service.ts`

Uses rendered prompts to call OpenRouter:

```typescript
import { LLMService } from '$lib/services/llm.service';

const llm = new LLMService();
const problem = await llm.generateProblem({
  age: 7,
  difficulty: 'easy',
  problemType: 'pattern',
  performanceHistory: [...]
});
```

---

## 📖 Template Variables

### generate-problem.yaml

| Variable | Type | Purpose |
|----------|------|---------|
| `age` | number | Child's age (4-10) |
| `difficulty` | string | Base difficulty ('easy'/'hard') |
| `initial_guidance` | string? | Optional adult-provided context |
| `problem_type` | string | 'pattern', 'category', 'comparison', 'grouping' |
| `performance_history` | array | Last 5 problems with results |
| `consecutive_correct` | number | Current success streak |
| `consecutive_incorrect` | number | Current failure streak |

### validate-problem.yaml

| Variable | Type | Purpose |
|----------|------|---------|
| `problem` | object | Generated problem to validate |
| `age` | number | Target age |

---

## 🎮 Used By

### Logic Lab Game

**Flow:**
```
Logic Lab Engine
  ↓
LLMService.generateProblem()
  ↓
PromptLoader.renderPrompt('generate-problem', variables)
  ↓
OpenRouter API (with rendered prompts)
  ↓
Parse JSON response → Problem object
```

**See:** [docs/LOGIC-LAB.md](../../../docs/LOGIC-LAB.md) for complete details

---

## ✏️ Modifying Prompts

### Changing Instructions

Edit the YAML file directly - **no code changes needed:**

```yaml
# src/lib/prompts/generate-problem.yaml

system_prompt: |
  Du bist ein kreativer und geduldiger Lehrer für Kinder.

  # Add new instructions here
  NEUE REGEL:
  - Verwende mehr Tiere in den Fragen

  # Modify existing sections
  SCHWIERIGKEITSGRADE (1-5):
  Level 3: ...
```

Restart the dev server and changes take effect immediately.

### Adding New Variables

1. **Pass variable from service:**

```typescript
// src/lib/services/logic-lab.service.ts
const rendered = loader.renderPrompt('generate-problem', {
  age: 7,
  newVariable: 'some value',  // Add here
  // ...
});
```

2. **Use in YAML template:**

```yaml
# src/lib/prompts/generate-problem.yaml
system_prompt: |
  NEUER KONTEXT:
  {{ newVariable }}
```

### Jinja2 Control Flow

```yaml
user_prompt: |
  {% if condition %}
    Do something
  {% elif other_condition %}
    Do something else
  {% else %}
    Default behavior
  {% endif %}

  {% for item in list %}
    - {{ item.property }}
  {% endfor %}
```

**See:** [Jinja2 Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)

---

## 🧪 Testing Prompt Changes

### 1. Direct Testing

```bash
# Start Logic Lab game in browser
npm run dev

# Open dev tools console
# Check LLM requests/responses
```

### 2. Test Different Models

```yaml
# Try different models in YAML
model: "anthropic/claude-3-5-sonnet"  # More powerful
model: "openai/gpt-4o"                # Different style
model: "google/gemini-2.5-flash"      # Fast & cheap (default)
```

### 3. Adjust Temperature

```yaml
temperature: 0.7   # More consistent
temperature: 0.9   # Default - good variety
temperature: 1.2   # Very creative, more variation
temperature: 1.5   # Maximum creativity
```

---

## 🚨 Important Notes

### Safety Rules in Prompts

Prompts include strict safety rules for kid-appropriate content:

```yaml
system_prompt: |
  STRIKTE SICHERHEITSREGELN:
  1. NUR kinderfreundliche Themen: Tiere, Natur, Farben, Formen
  2. KEINE Erwähnung von: Gewalt, Tod, Religion, Politik
  3. Wörter müssen für {{ age }}-jährige verständlich sein
```

**Never remove or weaken these rules!**

### JSON Response Format

All prompts expect structured JSON responses:

```yaml
response_format:
  type: "json_object"

system_prompt: |
  ANTWORTFORMAT (WICHTIG):
  Antworte NUR mit einem JSON-Objekt:
  {
    "type": "pattern",
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correctIndex": 1,
    "explanation": "...",
    "difficulty": 3
  }
```

LLMService validates this structure automatically.

---

## 📖 Related Files

| File | Purpose |
|------|---------|
| [src/lib/services/prompt-loader.service.ts](../services/prompt-loader.service.ts) | YAML + Jinja2 loader |
| [src/lib/services/llm.service.ts](../services/llm.service.ts) | OpenRouter API client |
| [src/lib/services/logic-lab.service.ts](../services/logic-lab.service.ts) | Game engine using prompts |
| [docs/LOGIC-LAB.md](../../../docs/LOGIC-LAB.md) | Complete Logic Lab documentation |

---

## 💡 Why YAML + Jinja2?

### Benefits

1. **Separation of Concerns:** Prompts are content, not code
2. **Easy Iteration:** Modify prompts without touching TypeScript
3. **Version Control:** Track prompt changes independently
4. **Reusability:** Same system for future LLM features
5. **Dynamic Content:** Loops and conditionals for complex logic
6. **Industry Standard:** Used by LangChain, LlamaIndex, etc.

### Alternatives Considered

- **Hardcoded strings:** Not maintainable for long prompts
- **LangChain:** Too heavy for our simple needs
- **Custom template engine:** Why reinvent the wheel?

---

**For implementation details, see code comments in `prompt-loader.service.ts` and `llm.service.ts`.**
