export type DifficultyLevel = 'easy' | 'hard';

export type GameType = 'verbal-memory' | 'visual-memory';

export interface User {
    _id?: string;
    name: string;
    createdAt: Date;
}

export interface GameSession {
    _id?: string;
    userId: string;
    gameType: GameType;
    difficulty: DifficultyLevel;
    score: number;
    lives: number;
    round: number;

    // Verbal memory specific (optional, only for verbal-memory games)
    wordsShown?: string[];
    seenWords?: Set<string>;
    currentWord?: string | null;
    previousWord?: string | null;
    isCurrentWordNew?: boolean;

    // Visual memory specific (optional, only for visual-memory games)
    visualMemoryState?: VisualMemoryGameState;

    isActive: boolean;
    startedAt: Date;
    endedAt?: Date;
}

export interface GameSessionDocument extends Omit<GameSession, 'seenWords'> {
    seenWords?: string[];
    currentWord?: string | null;
    previousWord?: string | null;
    isCurrentWordNew?: boolean;
    visualMemoryState?: VisualMemoryGameState;
}

export interface GameStats {
    totalGames: number;
    highScore: number;
    averageScore: number;
    lastPlayed?: Date;
}

export interface WordPool {
    easy: string[];
    hard: string[];
}

export interface VisualMemoryGameState {
    gridSize: number;
    targetCount: number;
    targetPositions: number[];
    userSelections: number[];
    presentationTime: number;
    retentionDelay: number;
}

export interface VisualMemoryDifficultyConfig {
    gridSize: number;
    startingTargets: number;
    maxTargets: number;
    presentationTime: number;
    retentionDelay: number;
}
