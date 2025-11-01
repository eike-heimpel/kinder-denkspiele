export type DifficultyLevel = 'easy' | 'hard';

export type GameType = 'verbal-memory' | 'visual-memory' | 'reaction-time' | 'logic-lab';

export interface User {
    _id?: string;
    name: string;
    avatar: string; // emoji avatar
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
    
    // Reaction time specific (optional, only for reaction-time games)
    reactionTimeState?: ReactionTimeGameState;

    // Logic Lab specific (optional, only for logic-lab games)
    logicLabState?: LogicLabGameState;

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
    reactionTimeState?: ReactionTimeGameState;
    logicLabState?: LogicLabGameState;
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

export interface ReactionTimeGameState {
    currentRound: number;
    totalRounds: number;
    reactionTimes: number[];
    minDelay: number;
    maxDelay: number;
    falseStarts: number;
}

export interface ReactionTimeDifficultyConfig {
    totalRounds: number;
    minDelay: number;
    maxDelay: number;
}

export type ProblemType = 'pattern' | 'category' | 'comparison' | 'grouping';

export interface Problem {
    id: string;
    type: ProblemType;
    question: string;
    options: string[];
    correctIndex: number;
    explanation: string;
    difficultyLevel: number;
    timestamp: Date;
    userAnswerIndex?: number;
    isCorrect?: boolean;
    responseTime?: number;
}

export interface LogicLabGameState {
    age: number; // Child's age (replaces difficulty)
    guidance: string; // Optional theme guidance
    modelName: string;
    currentProblem: Problem;
    problemHistory: Problem[]; // ALL problems ever asked (infinite)
    correctAnswers: number;
    consecutiveCorrect: number;
    consecutiveIncorrect: number;
    currentDifficultyLevel: number;
    hintsUsed: number;
    lastPlayedAt: Date; // Track when user last played
}
