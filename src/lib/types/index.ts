export type DifficultyLevel = 'easy' | 'hard';

export type GameType = 'verbal-memory';

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
    wordsShown: string[];
    seenWords: Set<string>;
    currentWord: string | null;
    previousWord: string | null;
    isCurrentWordNew: boolean;
    isActive: boolean;
    startedAt: Date;
    endedAt?: Date;
}

export interface GameSessionDocument extends Omit<GameSession, 'seenWords'> {
    seenWords: string[];
    currentWord: string | null;
    previousWord: string | null;
    isCurrentWordNew: boolean;
    round: number;
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
