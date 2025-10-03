# Human Benchmark - Deutsche Spiele für Kinder

Ein kinderfreundliches deutsches Spiel basierend auf Human Benchmark, entwickelt mit SvelteKit und Svelte 5.

---

## 🤖 For AI Agents

**START HERE:** [AI-GUIDE.md](./AI-GUIDE.md)

Complete documentation for AI agents includes:
- [AI-GUIDE.md](./AI-GUIDE.md) - Main entry point and navigation
- [TECH-STACK.md](./TECH-STACK.md) - Technical specifications
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [DECISIONS.md](./DECISIONS.md) - Why we made specific choices
- [API-REFERENCE.md](./API-REFERENCE.md) - Complete API documentation
- [THEMING.md](./THEMING.md) - UI customization guide

---

## 🎮 Features

- **Verbales Gedächtnis**: Teste dein Gedächtnis mit deutschen Wörtern
- **Zwei Schwierigkeitsgrade**: Einfach (für 5-6 Jahre) und Schwer (für 7-8 Jahre)
- **Mehrere Spieler**: Jedes Kind kann sein eigenes Profil haben
- **Statistiken-Seite**: Zeige historische Performance (Höchstwerte, Durchschnitt, Spiele gespielt)
- **Kid-Friendly UI**: Große Buttons, bunte Farben, einfache Navigation
- **Keine Duplikate**: Gleiches Wort nie zweimal hintereinander

## 🏗️ Architektur

Das Projekt folgt einer klaren Schichtenarchitektur:

```
src/
├── lib/
│   ├── types/              # TypeScript Typ-Definitionen
│   ├── db/                 # Datenbankverbindung
│   ├── repositories/       # Datenbank-Operationen (User, GameSession)
│   ├── services/           # Geschäftslogik (WordService, GameEngine)
│   ├── data/               # Statische Daten (Wortpools)
│   └── components/         # Wiederverwendbare UI-Komponenten
└── routes/
    ├── api/                # API-Endpunkte
    │   ├── users/
    │   └── game/verbal-memory/
    └── game/               # Spiel-Seiten
        └── verbal-memory/
```

### Schichten-Erklärung:

1. **Types Layer**: Definiert alle TypeScript-Typen und Interfaces
2. **Database Layer**: MongoDB-Verbindung und Client
3. **Repository Layer**: Abstrahiert Datenbank-Operationen
4. **Service Layer**: Beinhaltet Geschäftslogik und Spielmechanik
5. **API Layer**: SvelteKit Server-Endpunkte
6. **UI Layer**: Svelte 5 Komponenten und Seiten

## 🚀 Setup

### Voraussetzungen

- Node.js 24+ (oder 22.12+)
- Docker & Docker Compose
- npm oder pnpm

### Installation

1. **Repository klonen**
   ```bash
   cd humanbenchmark-german-kids
   ```

2. **Dependencies installieren**
   ```bash
   npm install
   ```

3. **Environment-Variablen einrichten**
   
   Erstelle eine `.env` Datei im Projekt-Root:
   ```bash
   MONGODB_URI=mongodb://localhost:27017/humanbenchmark
   ```

4. **MongoDB starten**
   ```bash
   docker-compose up -d
   ```

5. **Entwicklungsserver starten**
   ```bash
   npm run dev
   ```

6. **Öffne den Browser**
   
   Navigiere zu `http://localhost:5173`

## 🎯 Verwendung

1. **Spieler erstellen**: Klicke auf "Neuer Spieler" und gib einen Namen ein
2. **Spieler auswählen**: Wähle einen Spieler aus der Liste
3. **Spiel starten**: Wähle "Verbales Gedächtnis" und einen Schwierigkeitsgrad
4. **Spielen**: Entscheide, ob du jedes Wort schon gesehen hast oder nicht
   - Tastatur: `←` oder `N` für NEU, `→` oder `G` für GESEHEN
   - Oder klicke die großen Buttons
5. **Statistiken ansehen**: Klicke "Statistiken ansehen" um historische Performance zu sehen

## 📦 Erweiterbarkeit

### Neue Spiele hinzufügen

1. **Typ hinzufügen**: In `src/lib/types/index.ts`
   ```typescript
   export type GameType = 'verbal-memory' | 'reaction-time';
   ```

2. **Service erstellen**: In `src/lib/services/`
   ```typescript
   export class ReactionTimeEngine { ... }
   ```

3. **API-Endpunkte**: In `src/routes/api/game/reaction-time/`

4. **UI-Komponente**: In `src/routes/game/reaction-time/`

### Wortpools erweitern

Bearbeite `src/lib/data/word-pools.ts`:
```typescript
export const germanWordPools: WordPool = {
  easy: [...],
  hard: [...]
};
```

### Neue Repository-Methoden

Erweitere `src/lib/repositories/`:
```typescript
async getLeaderboard(gameType: GameType): Promise<User[]> {
  // Implementation
}
```

## 🛠️ Tech Stack

- **SvelteKit**: Full-stack Framework
- **Svelte 5**: UI Framework (mit Runes)
- **TypeScript**: Type Safety
- **Tailwind CSS**: Styling
- **MongoDB**: Datenbank
- **Docker**: Containerisierung

## 📝 API-Endpunkte

### Users
- `GET /api/users` - Alle Benutzer abrufen
- `POST /api/users` - Neuen Benutzer erstellen
- `GET /api/users/[id]` - Benutzer nach ID
- `DELETE /api/users/[id]` - Benutzer löschen

### Verbal Memory Game
- `POST /api/game/verbal-memory/start` - Spiel starten
- `POST /api/game/verbal-memory/answer` - Antwort senden
- `GET /api/game/verbal-memory/stats` - Statistiken abrufen

## 🔧 Scripts

```bash
npm run dev          # Entwicklungsserver starten
npm run build        # Produktions-Build erstellen
npm run preview      # Produktions-Build testen
npm run check        # TypeScript type checking
```

## 📄 Lizenz

Dieses Projekt ist für persönlichen Gebrauch bestimmt.
