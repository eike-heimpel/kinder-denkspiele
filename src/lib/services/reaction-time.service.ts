import type { 
    GameSession, 
    DifficultyLevel, 
    ReactionTimeGameState,
    ReactionTimeDifficultyConfig 
} from '$lib/types';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';

export class ReactionTimeEngine {
    private repository: GameSessionRepository;
    
    private static readonly DIFFICULTY_CONFIGS: Record<DifficultyLevel, ReactionTimeDifficultyConfig> = {
        easy: {
            totalRounds: 5,
            minDelay: 2000,
            maxDelay: 4000
        },
        hard: {
            totalRounds: 5,
            minDelay: 1000,
            maxDelay: 3000
        }
    };

    constructor(repository?: GameSessionRepository) {
        this.repository = repository || new GameSessionRepository();
    }

    async startGame(userId: string, difficulty: DifficultyLevel): Promise<GameSession> {
        const config = ReactionTimeEngine.DIFFICULTY_CONFIGS[difficulty];
        
        const gameSession: GameSession = {
            userId,
            gameType: 'reaction-time',
            difficulty,
            score: 0,
            lives: 1,
            round: 1,
            reactionTimeState: {
                currentRound: 1,
                totalRounds: config.totalRounds,
                reactionTimes: [],
                minDelay: config.minDelay,
                maxDelay: config.maxDelay,
                falseStarts: 0
            },
            isActive: true,
            startedAt: new Date()
        };

        const savedSession = await this.repository.create(gameSession);
        return savedSession;
    }

    async submitReaction(sessionId: string, reactionTime: number, isFalseStart: boolean): Promise<GameSession> {
        const session = await this.repository.findById(sessionId);
        
        if (!session || !session.isActive) {
            throw new Error('Invalid or inactive game session');
        }

        if (!session.reactionTimeState) {
            throw new Error('Not a reaction time game session');
        }

        const state = session.reactionTimeState;

        if (isFalseStart) {
            state.falseStarts += 1;
        } else {
            state.reactionTimes.push(reactionTime);
            state.currentRound += 1;
        }

        if (state.currentRound > state.totalRounds) {
            session.isActive = false;
            session.endedAt = new Date();
            session.score = this.calculateAverageReactionTime(state.reactionTimes);
        }

        await this.repository.update(sessionId, session);
        return session;
    }

    private calculateAverageReactionTime(times: number[]): number {
        if (times.length === 0) return 0;
        const sum = times.reduce((a, b) => a + b, 0);
        return Math.round(sum / times.length);
    }

    async getStats(userId: string, difficulty?: DifficultyLevel) {
        if (difficulty) {
            return this.repository.getStatsByUser(userId, 'reaction-time', difficulty);
        }
        
        const easyStats = await this.repository.getStatsByUser(userId, 'reaction-time', 'easy');
        const hardStats = await this.repository.getStatsByUser(userId, 'reaction-time', 'hard');
        
        return {
            easy: easyStats,
            hard: hardStats
        };
    }

    async loadGame(sessionId: string): Promise<GameSession> {
        const session = await this.repository.findById(sessionId);
        if (!session) {
            throw new Error('Game session not found');
        }
        return session;
    }

    static getDifficultyConfig(difficulty: DifficultyLevel): ReactionTimeDifficultyConfig {
        return ReactionTimeEngine.DIFFICULTY_CONFIGS[difficulty];
    }

    generateDelay(minDelay: number, maxDelay: number): number {
        return Math.floor(Math.random() * (maxDelay - minDelay + 1)) + minDelay;
    }
}

