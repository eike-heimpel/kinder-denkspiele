import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ReactionTimeEngine } from './reaction-time.service';

// Mock the repository
vi.mock('$lib/repositories/game-session.repository', () => ({
    GameSessionRepository: class {
        private sessions = new Map();
        private idCounter = 0;

        async create(session: any) {
            const id = (++this.idCounter).toString();
            const newSession = { ...session, _id: id };
            this.sessions.set(id, newSession);
            return newSession;
        }

        async update(id: string, updates: any) {
            const session = this.sessions.get(id);
            if (session) {
                // Deep merge for nested objects like reactionTimeState
                Object.keys(updates).forEach(key => {
                    if (key === 'reactionTimeState' && updates[key]) {
                        session[key] = { ...session[key], ...updates[key] };
                    } else {
                        session[key] = updates[key];
                    }
                });
            }
        }

        async findById(id: string) {
            const session = this.sessions.get(id);
            if (!session) return null;
            return { ...session };
        }

        async getStatsByGameType() {
            return {
                totalGames: 0,
                highScore: 0,
                averageScore: 0
            };
        }
    }
}));

describe('ReactionTimeEngine', () => {
    let engine: ReactionTimeEngine;

    beforeEach(() => {
        engine = new ReactionTimeEngine();
    });

    describe('startGame', () => {
        it('should start an easy game with correct config', async () => {
            const gameState = await engine.startGame('user123', 'easy');

            expect(gameState.userId).toBe('user123');
            expect(gameState.gameType).toBe('reaction-time');
            expect(gameState.difficulty).toBe('easy');
            expect(gameState.score).toBe(0);
            expect(gameState.round).toBe(1);
            expect(gameState.isActive).toBe(true);
            expect(gameState.reactionTimeState).toBeDefined();
            expect(gameState.reactionTimeState?.currentRound).toBe(1);
            expect(gameState.reactionTimeState?.totalRounds).toBe(5);
            expect(gameState.reactionTimeState?.minDelay).toBe(2000);
            expect(gameState.reactionTimeState?.maxDelay).toBe(4000);
            expect(gameState.reactionTimeState?.reactionTimes).toEqual([]);
            expect(gameState.reactionTimeState?.falseStarts).toBe(0);
        });

        it('should start a hard game with shorter delays', async () => {
            const gameState = await engine.startGame('user123', 'hard');

            expect(gameState.difficulty).toBe('hard');
            expect(gameState.reactionTimeState?.minDelay).toBe(1000);
            expect(gameState.reactionTimeState?.maxDelay).toBe(3000);
        });

        it('should have startedAt timestamp', async () => {
            const before = new Date();
            const gameState = await engine.startGame('user123', 'easy');
            const after = new Date();

            expect(gameState.startedAt).toBeDefined();
            expect(gameState.startedAt!.getTime()).toBeGreaterThanOrEqual(before.getTime());
            expect(gameState.startedAt!.getTime()).toBeLessThanOrEqual(after.getTime());
        });
    });

    describe('submitReaction', () => {
        it('should record a reaction time and advance round', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            const updated = await engine.submitReaction(sessionId, 250, false);

            expect(updated.reactionTimeState?.reactionTimes).toEqual([250]);
            expect(updated.reactionTimeState?.currentRound).toBe(2);
            expect(updated.score).toBe(250); // Average of [250]
            expect(updated.isActive).toBe(true);
        });

        it('should calculate average score correctly', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 300, false);
            const updated = await engine.submitReaction(sessionId, 250, false);

            expect(updated.reactionTimeState?.reactionTimes).toEqual([200, 300, 250]);
            expect(updated.score).toBe(250); // Average of [200, 300, 250] = 750/3 = 250
        });

        it('should record false starts without advancing round', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            const updated = await engine.submitReaction(sessionId, 0, true);

            expect(updated.reactionTimeState?.falseStarts).toBe(1);
            expect(updated.reactionTimeState?.reactionTimes).toEqual([]);
            expect(updated.reactionTimeState?.currentRound).toBe(1); // Should not advance
            expect(updated.score).toBe(0); // No reaction times recorded
        });

        it('should handle multiple false starts', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 0, true);
            await engine.submitReaction(sessionId, 0, true);
            const updated = await engine.submitReaction(sessionId, 0, true);

            expect(updated.reactionTimeState?.falseStarts).toBe(3);
            expect(updated.reactionTimeState?.currentRound).toBe(1);
        });

        it('should end game after 5 successful reactions', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 220, false);
            await engine.submitReaction(sessionId, 240, false);
            await engine.submitReaction(sessionId, 260, false);
            const final = await engine.submitReaction(sessionId, 280, false);

            expect(final.isActive).toBe(false);
            expect(final.endedAt).toBeDefined();
            expect(final.reactionTimeState?.reactionTimes).toEqual([200, 220, 240, 260, 280]);
            expect(final.score).toBe(240); // Average of all times
        });

        it('should continue game if false starts mixed with reactions', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 200, false); // Round 1
            await engine.submitReaction(sessionId, 0, true);    // False start
            await engine.submitReaction(sessionId, 250, false); // Round 2
            const updated = await engine.submitReaction(sessionId, 0, true); // False start

            expect(updated.reactionTimeState?.reactionTimes).toEqual([200, 250]);
            expect(updated.reactionTimeState?.falseStarts).toBe(2);
            expect(updated.reactionTimeState?.currentRound).toBe(3);
            expect(updated.isActive).toBe(true);
        });

        it('should throw error for invalid session', async () => {
            await expect(
                engine.submitReaction('invalid-id', 250, false)
            ).rejects.toThrow('Invalid or inactive game session');
        });

        it('should throw error for inactive session', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            // Complete the game
            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 200, false);

            // Try to submit another reaction
            await expect(
                engine.submitReaction(sessionId, 250, false)
            ).rejects.toThrow('Invalid or inactive game session');
        });
    });

    describe('score calculation', () => {
        it('should round average to nearest integer', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 100, false);
            await engine.submitReaction(sessionId, 150, false);
            const updated = await engine.submitReaction(sessionId, 200, false);

            // Average = (100 + 150 + 200) / 3 = 150
            expect(updated.score).toBe(150);
        });

        it('should handle rounding correctly for decimals', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 100, false);
            await engine.submitReaction(sessionId, 101, false);
            const updated = await engine.submitReaction(sessionId, 102, false);

            // Average = (100 + 101 + 102) / 3 = 101
            expect(updated.score).toBe(101);
        });

        it('should ignore false starts in score calculation', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            await engine.submitReaction(sessionId, 0, true); // False start
            await engine.submitReaction(sessionId, 200, false);
            await engine.submitReaction(sessionId, 0, true); // False start
            const updated = await engine.submitReaction(sessionId, 300, false);

            // Average should only be (200 + 300) / 2 = 250
            expect(updated.score).toBe(250);
            expect(updated.reactionTimeState?.reactionTimes).toEqual([200, 300]);
        });
    });

    describe('loadGame', () => {
        it('should load an existing game session', async () => {
            const created = await engine.startGame('user123', 'easy');
            const sessionId = created._id!;

            await engine.submitReaction(sessionId, 250, false);
            const loaded = await engine.loadGame(sessionId);

            expect(loaded._id).toBe(sessionId);
            expect(loaded.reactionTimeState?.reactionTimes).toEqual([250]);
            expect(loaded.reactionTimeState?.currentRound).toBe(2);
        });

        it('should throw error for non-existent session', async () => {
            await expect(
                engine.loadGame('non-existent-id')
            ).rejects.toThrow('Game session not found');
        });
    });

    describe('edge cases', () => {
        it('should handle very fast reaction times', async () => {
            const gameState = await engine.startGame('user123', 'hard');
            const sessionId = gameState._id!;

            const updated = await engine.submitReaction(sessionId, 50, false);

            expect(updated.reactionTimeState?.reactionTimes).toEqual([50]);
            expect(updated.score).toBe(50);
        });

        it('should handle very slow reaction times', async () => {
            const gameState = await engine.startGame('user123', 'easy');
            const sessionId = gameState._id!;

            const updated = await engine.submitReaction(sessionId, 5000, false);

            expect(updated.reactionTimeState?.reactionTimes).toEqual([5000]);
            expect(updated.score).toBe(5000);
        });

        it('should maintain round count correctly across sessions', async () => {
            const game1 = await engine.startGame('user1', 'easy');
            const game2 = await engine.startGame('user2', 'hard');

            await engine.submitReaction(game1._id!, 200, false);
            await engine.submitReaction(game2._id!, 150, false);
            await engine.submitReaction(game1._id!, 250, false);

            const loaded1 = await engine.loadGame(game1._id!);
            const loaded2 = await engine.loadGame(game2._id!);

            expect(loaded1.reactionTimeState?.currentRound).toBe(3);
            expect(loaded2.reactionTimeState?.currentRound).toBe(2);
        });
    });
});

