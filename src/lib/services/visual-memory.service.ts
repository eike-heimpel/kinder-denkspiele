import type {
    GameSession,
    DifficultyLevel,
    VisualMemoryGameState,
    VisualMemoryDifficultyConfig
} from '$lib/types';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';

export class VisualMemoryEngine {
    private repository: GameSessionRepository;

    private static readonly DIFFICULTY_CONFIGS: Record<DifficultyLevel, VisualMemoryDifficultyConfig> = {
        easy: {
            gridSize: 3,
            startingTargets: 2,
            maxTargets: 5,
            presentationTime: 2000,
            retentionDelay: 500
        },
        hard: {
            gridSize: 4,
            startingTargets: 3,
            maxTargets: 7,
            presentationTime: 1500,
            retentionDelay: 1000
        }
    };

    constructor(repository?: GameSessionRepository) {
        this.repository = repository || new GameSessionRepository();
    }

    async startGame(userId: string, difficulty: DifficultyLevel): Promise<GameSession> {
        const config = VisualMemoryEngine.DIFFICULTY_CONFIGS[difficulty];

        const gameSession: GameSession = {
            userId,
            gameType: 'visual-memory',
            difficulty,
            score: 0,
            lives: 3,
            round: 1,
            visualMemoryState: {
                gridSize: config.gridSize,
                targetCount: config.startingTargets,
                targetPositions: this.generateRandomPositions(
                    config.gridSize * config.gridSize,
                    config.startingTargets
                ),
                userSelections: [],
                presentationTime: config.presentationTime,
                retentionDelay: config.retentionDelay
            },
            isActive: true,
            startedAt: new Date()
        };

        const savedSession = await this.repository.create(gameSession);
        return savedSession;
    }

    private generateRandomPositions(gridTotal: number, count: number): number[] {
        const positions: number[] = [];
        const available = Array.from({ length: gridTotal }, (_, i) => i);

        for (let i = 0; i < count; i++) {
            const randomIndex = Math.floor(Math.random() * available.length);
            positions.push(available[randomIndex]);
            available.splice(randomIndex, 1);
        }

        return positions.sort((a, b) => a - b);
    }

    async submitAnswer(sessionId: string, userSelections: number[]): Promise<{
        session: GameSession;
        previousTargets: number[];
        isCorrect: boolean;
    }> {
        const session = await this.repository.findById(sessionId);

        if (!session || !session.isActive) {
            throw new Error('Invalid or inactive game session');
        }

        if (!session.visualMemoryState) {
            throw new Error('Not a visual memory game session');
        }

        const state = session.visualMemoryState;
        const previousTargets = [...state.targetPositions];
        const isCorrect = this.validateAnswer(state.targetPositions, userSelections);

        if (isCorrect) {
            session.score += 1;
            session.round += 1;

            const newTargetCount = this.calculateNextTargetCount(
                session.difficulty,
                session.round,
                state.targetCount
            );

            state.targetCount = newTargetCount;
            state.targetPositions = this.generateRandomPositions(
                state.gridSize * state.gridSize,
                newTargetCount
            );
            state.userSelections = [];

        } else {
            session.lives -= 1;

            if (session.lives <= 0) {
                session.isActive = false;
                session.endedAt = new Date();
            } else {
                state.targetPositions = this.generateRandomPositions(
                    state.gridSize * state.gridSize,
                    state.targetCount
                );
                state.userSelections = [];
            }
        }

        await this.repository.update(sessionId, session);
        return {
            session,
            previousTargets,
            isCorrect
        };
    }

    private validateAnswer(targets: number[], userSelections: number[]): boolean {
        if (targets.length !== userSelections.length) {
            return false;
        }

        const sortedTargets = [...targets].sort((a, b) => a - b);
        const sortedSelections = [...userSelections].sort((a, b) => a - b);

        return sortedTargets.every((target, index) => target === sortedSelections[index]);
    }

    private calculateNextTargetCount(
        difficulty: DifficultyLevel,
        round: number,
        currentCount: number
    ): number {
        const config = VisualMemoryEngine.DIFFICULTY_CONFIGS[difficulty];

        const baseIncrease = Math.floor((round - 1) / 2);
        const newCount = config.startingTargets + baseIncrease;

        return Math.min(newCount, config.maxTargets);
    }

    async getStats(userId: string, difficulty?: DifficultyLevel) {
        if (difficulty) {
            return this.repository.getStatsByUser(userId, 'visual-memory', difficulty);
        }

        const easyStats = await this.repository.getStatsByUser(userId, 'visual-memory', 'easy');
        const hardStats = await this.repository.getStatsByUser(userId, 'visual-memory', 'hard');

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

    static getDifficultyConfig(difficulty: DifficultyLevel): VisualMemoryDifficultyConfig {
        return VisualMemoryEngine.DIFFICULTY_CONFIGS[difficulty];
    }
}

