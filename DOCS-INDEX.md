---
title: "Documentation Index"
purpose: "Central index for all AI agent documentation"
audience: "AI agents"
last_updated: "2025-10-03"
version: "2.0"
keywords: ["documentation", "index", "navigation", "guide"]
---

# 📚 Documentation Index

**Total Documentation:** ~120KB across 16 files  
**Target Audience:** AI Agents and Future Developers  
**Last Updated:** 2025-10-03  
**Version:** 2.0 (Hierarchical module documentation)

---

## 🎯 Quick Start

**New to this codebase?** Start here:
1. Read [CLAUDE.md](./CLAUDE.md) (16KB) - **MAIN ENTRY POINT**
2. Skim [ARCHITECTURE.md](./ARCHITECTURE.md) (11KB) - Understand the system
3. Run through [QUICKSTART.md](./QUICKSTART.md) (5KB) - Get it running

**Need to make changes?** Check:
1. **Module-specific CLAUDE.md files** (see below) - Focused context
2. [TECH-STACK.md](./TECH-STACK.md) (13KB) - Tech details
3. [API-REFERENCE.md](./API-REFERENCE.md) (13KB) - Endpoint specs
4. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) (12KB) - When things break

**Why is it built this way?**
1. [DECISIONS.md](./DECISIONS.md) (15KB) - Technical rationale

**Want to change colors/design?**
1. [THEMING.md](./THEMING.md) (7KB) - Customization guide

---

## 📂 Module-Level Documentation (NEW)

### Core Library (`src/lib/`)
- **[src/lib/CLAUDE.md](./src/lib/CLAUDE.md)** (5KB) - Shared utilities, types, data layer
- **[src/lib/services/CLAUDE.md](./src/lib/services/CLAUDE.md)** (10KB) - Game engines & business logic
- **[src/lib/components/CLAUDE.md](./src/lib/components/CLAUDE.md)** (8KB) - Reusable UI components
- **[src/lib/repositories/CLAUDE.md](./src/lib/repositories/CLAUDE.md)** (9KB) - Database operations

### Routes (`src/routes/`)
- **[src/routes/CLAUDE.md](./src/routes/CLAUDE.md)** (6KB) - Routing structure overview
- **[src/routes/api/CLAUDE.md](./src/routes/api/CLAUDE.md)** (11KB) - API endpoint implementation
- **[src/routes/game/CLAUDE.md](./src/routes/game/CLAUDE.md)** (10KB) - Game page components & UI logic

**💡 Tip:** When working on a specific module, read its CLAUDE.md for focused, relevant context.

---

## 📖 Documentation Overview

### AI-GUIDE.md (15KB)
**Purpose:** Primary entry point for AI agents  
**Contains:**
- Complete navigation to all other docs
- Core concepts (Svelte 5 runes, Tailwind v4, layered architecture)
- Quick reference tables
- Common tasks with step-by-step instructions
- Data flow examples
- Critical gotchas

**When to Read:** Always start here

---

### TECH-STACK.md (12KB)
**Purpose:** Deep technical specifications  
**Contains:**
- SvelteKit 2.x details and patterns
- Svelte 5 runes complete reference
- Tailwind CSS v4 configuration
- MongoDB driver usage
- TypeScript patterns
- Vite configuration
- Environment variables
- Version constraints

**When to Read:** 
- Before making technical changes
- When encountering version issues
- To understand framework-specific patterns

---

### ARCHITECTURE.md (10KB)
**Purpose:** System design and structure  
**Contains:**
- Layered architecture explanation
- Data flow diagrams
- Design patterns used
- Component architecture
- Database schema
- API design principles
- Extension points for new features

**When to Read:**
- To understand overall system
- Before adding new features
- When refactoring

---

### API-REFERENCE.md (12KB)
**Purpose:** Complete API endpoint documentation  
**Contains:**
- All endpoints with examples
- Request/response formats
- Error codes and messages
- Query parameters
- Testing examples with curl
- Future planned endpoints

**When to Read:**
- Before calling any API
- When implementing new endpoints
- To understand data contracts

---

### TROUBLESHOOTING.md (11KB)
**Purpose:** Solutions to common problems  
**Contains:**
- Critical issues (Tailwind, MongoDB, Svelte 5)
- Common development issues
- Debugging techniques
- Error message interpretations
- Prevention strategies

**When to Read:**
- When something breaks
- Before asking for help
- After encountering an error

---

### DECISIONS.md (14KB)
**Purpose:** Technical rationale and context  
**Contains:**
- Why we chose each technology
- Architectural decision justifications
- Feature decisions explained
- Trade-offs and alternatives considered
- Lessons learned
- Future considerations

**When to Read:**
- To understand "why" not just "what"
- Before making major changes
- When questioning existing patterns

---

### THEMING.md (6KB)
**Purpose:** UI customization guide  
**Contains:**
- Color scheme changes
- Component styling
- Animation customization
- Tailwind patterns used
- Quick theme presets

**When to Read:**
- When changing design
- To customize colors/fonts
- Before adding UI components

---

### QUICKSTART.md (4KB)
**Purpose:** Get up and running fast  
**Contains:**
- Setup steps
- Management commands
- Testing instructions
- Project structure overview
- Next steps

**When to Read:**
- First time setting up
- As quick reference
- To verify setup

---

### README.md (5KB)
**Purpose:** Human-readable project overview  
**Contains:**
- Feature list
- Architecture overview
- Setup instructions
- API endpoints list
- Customization basics

**When to Read:**
- For general project information
- To share with others
- As starting point before diving deep

---

## 🏗️ Documentation Architecture

This project uses **hierarchical module documentation** to provide focused, contextual information:

### Structure

```
Root Documentation (High-Level)
├── CLAUDE.md (Entry point with Q&A and navigation)
├── ARCHITECTURE.md (System design)
├── API-REFERENCE.md (Complete API specs)
├── TECH-STACK.md (Technology details)
└── ... (other root docs)

Module Documentation (Focused)
├── src/lib/CLAUDE.md (Lib layer overview)
│   ├── src/lib/services/CLAUDE.md (Business logic)
│   ├── src/lib/components/CLAUDE.md (UI components)
│   └── src/lib/repositories/CLAUDE.md (Data access)
│
└── src/routes/CLAUDE.md (Routes overview)
    ├── src/routes/api/CLAUDE.md (API endpoints)
    └── src/routes/game/CLAUDE.md (Game pages)
```

### Benefits

1. **Focused Context:** Get only relevant information for the module you're working on
2. **Reduced Cognitive Load:** Smaller, targeted docs instead of monolithic files
3. **Better Navigation:** Clear hierarchy with cross-references
4. **Scalability:** Easy to add docs as codebase grows

### Usage Pattern

1. Start at [CLAUDE.md](./CLAUDE.md) for overview and navigation
2. Navigate to specific module CLAUDE.md for focused context
3. Reference root-level docs for comprehensive information
4. Use Q&A section in CLAUDE.md for quick lookups

---

## 🔍 Finding Information

### By Topic

**Svelte 5:**
- Runes → [TECH-STACK.md](./TECH-STACK.md#svelte-5-runes)
- Component patterns → [AI-GUIDE.md](./AI-GUIDE.md#svelte-5-runes)
- Troubleshooting → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#svelte-5-syntax-errors)

**Tailwind CSS:**
- Configuration → [TECH-STACK.md](./TECH-STACK.md#tailwind-css-v4)
- Customization → [THEMING.md](./THEMING.md)
- Not working? → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#tailwind-css-not-working)

**MongoDB:**
- Setup → [QUICKSTART.md](./QUICKSTART.md#start-everything)
- Patterns → [TECH-STACK.md](./TECH-STACK.md#mongodb)
- Issues → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#mongodb-connection-failed)

**API:**
- Complete reference → [API-REFERENCE.md](./API-REFERENCE.md)
- Design principles → [ARCHITECTURE.md](./ARCHITECTURE.md#api-design)
- Testing → [API-REFERENCE.md](./API-REFERENCE.md#testing)

**Adding Features:**
- New game → [AI-GUIDE.md](./AI-GUIDE.md#adding-a-new-game)
- Extension points → [ARCHITECTURE.md](./ARCHITECTURE.md#extension-points)
- Patterns to follow → [DECISIONS.md](./DECISIONS.md#architecture-decisions)

---

## 📊 Documentation Stats

### Root-Level Documentation

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| CLAUDE.md | 16KB | 700+ | Main entry point with Q&A |
| DECISIONS.md | 15KB | 650+ | Technical rationale |
| TECH-STACK.md | 13KB | 550+ | Technology details |
| API-REFERENCE.md | 13KB | 600+ | API documentation |
| TROUBLESHOOTING.md | 12KB | 500+ | Problem solving |
| ARCHITECTURE.md | 11KB | 400+ | System design |
| THEMING.md | 7KB | 260+ | UI customization |
| README.md | 5KB | 165+ | General overview |
| QUICKSTART.md | 5KB | 170+ | Quick setup |

**Root Total:** ~97KB

### Module-Level Documentation

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| src/routes/api/CLAUDE.md | 11KB | 500+ | API endpoint implementation |
| src/routes/game/CLAUDE.md | 10KB | 450+ | Game page components |
| src/lib/services/CLAUDE.md | 10KB | 500+ | Business logic layer |
| src/lib/repositories/CLAUDE.md | 9KB | 400+ | Data access layer |
| src/lib/components/CLAUDE.md | 8KB | 400+ | UI components |
| src/routes/CLAUDE.md | 6KB | 350+ | Routes overview |
| src/lib/CLAUDE.md | 5KB | 300+ | Lib layer overview |

**Module Total:** ~59KB

**Grand Total:** ~156KB of AI-optimized hierarchical documentation across 16 files

---

## 🎯 Documentation Principles

### 1. Precision
- Exact version numbers
- Specific file paths
- Complete code examples
- Clear error messages

### 2. Context
- Why decisions were made
- Trade-offs explained
- Alternatives considered
- Related information linked

### 3. Navigation
- Cross-referenced docs
- Clear section headers
- Table of contents
- Related docs listed

### 4. Searchability
- Consistent terminology
- Multiple search terms
- Code examples
- Error messages included

### 5. Completeness
- All technologies covered
- Common patterns documented
- Edge cases explained
- Future plans mentioned

---

## 🔄 Maintenance

### Updating Documentation

**When code changes:**
1. Update affected docs immediately
2. Check cross-references
3. Update version numbers
4. Test examples

**When adding features:**
1. Update AI-GUIDE with new task
2. Add to API-REFERENCE if needed
3. Update ARCHITECTURE if pattern changes
4. Document decision in DECISIONS

**When fixing bugs:**
1. Add to TROUBLESHOOTING
2. Explain root cause
3. Provide prevention tips

---

## 🎓 Best Practices

### For AI Agents
1. Always read AI-GUIDE.md first
2. Follow layer architecture strictly
3. Check TROUBLESHOOTING before asking
4. Document new decisions
5. Update relevant docs when changing code

### For Developers
1. Treat docs as code (version control)
2. Update docs with code changes
3. Add examples for complex patterns
4. Explain "why" not just "how"
5. Cross-reference related sections

---

## 📞 Quick Links

**Setup:**
- [Quick Setup](./QUICKSTART.md#setup)
- [Docker MongoDB](./QUICKSTART.md#management-commands)

**Development:**
- [Common Tasks](./AI-GUIDE.md#common-tasks)
- [Code Standards](./AI-GUIDE.md#coding-standards)
- [Dev Workflow](./AI-GUIDE.md#development-workflow)

**Reference:**
- [API Endpoints](./API-REFERENCE.md#table-of-contents)
- [Type Definitions](./TECH-STACK.md#typescript)
- [Database Schema](./TECH-STACK.md#mongodb)

**Customization:**
- [Theme Colors](./THEMING.md#change-primary-colors)
- [UI Components](./THEMING.md#component-specific-styling)
- [Word Pools](./AI-GUIDE.md#modifying-word-pools)

---

## ✅ Documentation Checklist

Before starting work:
- [ ] Read AI-GUIDE.md
- [ ] Understand relevant architecture
- [ ] Check tech stack details
- [ ] Review API contracts

While working:
- [ ] Follow documented patterns
- [ ] Check troubleshooting if stuck
- [ ] Reference decisions for context

After changes:
- [ ] Update affected docs
- [ ] Add examples if needed
- [ ] Test documented procedures
- [ ] Commit docs with code

---

**Remember:** Documentation is for future you (or future AI) who has no context. Be precise, be complete, be clear.

**Happy Coding! 🤖**
