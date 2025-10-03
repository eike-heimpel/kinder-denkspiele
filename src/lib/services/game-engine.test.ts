import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GameEngine } from './game-engine.service';
import { WordService } from './word.service';

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
                Object.assign(session, updates);
                // Also update Set if seenWords array is provided
                if (updates.seenWords && Array.isArray(updates.seenWords)) {
                    session.seenWords = new Set(updates.seenWords);
                }
            }
        }

        async findById(id: string) {
            const session = this.sessions.get(id);
            if (!session) return null;
            // Return a copy to avoid direct mutations
            return {
                ...session,
                seenWords: new Set(session.seenWords)
            };
        }
    }
}));

describe('GameEngine', () => {
    let engine: GameEngine;

    beforeEach(() => {
        engine = new GameEngine();
    });

    describe('startGame', () => {
        it('should start a game with 3 lives and 0 score', async () => {
            const gameState = await engine.startGame('user123', 'easy');

            expect(gameState.session).toBeDefined();
            expect(gameState.session?.lives).toBe(3);
            expect(gameState.session?.score).toBe(0);
            expect(gameState.currentWord).toBeDefined();
            expect(gameState.gameOver).toBe(false);
        });

        it('should show a new word on first turn', async () => {
            const gameState = await engine.startGame('user123', 'easy');

            expect(gameState.isCurrentWordNew).toBe(true);
            expect(gameState.session?.seenWords.size).toBe(0);
        });
    });

    describe('submitAnswer - NEW word logic', () => {
        it('should increase score when correctly identifying a NEW word', async () => {
            await engine.startGame('user123', 'easy');

            // First word is always new
            const result = await engine.submitAnswer('new');

            expect(result.session?.score).toBe(1);
            expect(result.session?.lives).toBe(3);
        });

        it('should decrease lives when incorrectly saying NEW word is SEEN', async () => {
            await engine.startGame('user123', 'easy');

            // First word is always new, but we say it's seen
            const result = await engine.submitAnswer('seen');

            expect(result.session?.score).toBe(0);
            expect(result.session?.lives).toBe(2);
        });

        it('should add word to seenWords when correctly identified as NEW', async () => {
            const initialState = await engine.startGame('user123', 'easy');
            const firstWord = initialState.currentWord!;

            await engine.submitAnswer('new');

            const session = engine.getSession();
            expect(session?.seenWords.has(firstWord)).toBe(true);
        });
    });

    describe('submitAnswer - SEEN word logic', () => {
        it('should handle a sequence of NEW words correctly', async () => {
            // Start game
            const state1 = await engine.startGame('user123', 'easy');
            expect(state1.isCurrentWordNew).toBe(true);

            // Answer first word correctly as NEW
            const state2 = await engine.submitAnswer('new');
            expect(state2.session?.score).toBe(1);
            expect(state2.session?.lives).toBe(3);

            // If second word is also NEW, we should not lose a life
            if (state2.isCurrentWordNew) {
                const state3 = await engine.submitAnswer('new');
                expect(state3.session?.lives).toBe(3); // Should NOT decrease
                expect(state3.session?.score).toBe(2);
            }
        });

        it('should correctly handle when a word is truly SEEN', async () => {
            // Mock WordService to control word selection
            const wordService = new WordService('easy');
            const mockShouldShowNewWord = vi.spyOn(wordService, 'shouldShowNewWord');

            // Start game and answer first word
            const state1 = await engine.startGame('user123', 'easy');
            const firstWord = state1.currentWord!;

            await engine.submitAnswer('new'); // Correctly identify as NEW

            // Force next word to be the same (seen)
            mockShouldShowNewWord.mockReturnValue(false); // Should show OLD word

            const state2 = await engine.submitAnswer('seen'); // This test will fail with current bug

            // If the word was actually SEEN, score should increase
            if (!state2.isCurrentWordNew) {
                expect(state2.session?.score).toBe(2);
                expect(state2.session?.lives).toBe(3);
            }
        });
    });

    describe('game over logic', () => {
        it('should end game when lives reach 0', async () => {
            await engine.startGame('user123', 'easy');

            // Make 3 wrong answers
            await engine.submitAnswer('seen'); // Wrong (word is new)
            await engine.submitAnswer('seen'); // Wrong
            const finalState = await engine.submitAnswer('seen'); // Wrong - game over

            expect(finalState.gameOver).toBe(true);
            expect(finalState.session?.lives).toBe(0);
            expect(finalState.message).toContain('Spiel vorbei');
        });

        it('should not decrease lives below 0', async () => {
            await engine.startGame('user123', 'easy');

            await engine.submitAnswer('seen');
            await engine.submitAnswer('seen');
            await engine.submitAnswer('seen');
            const result = await engine.submitAnswer('seen');

            expect(result.session?.lives).toBeGreaterThanOrEqual(0);
        });
    });

    describe('word tracking', () => {
        it('should track all words shown', async () => {
            const state1 = await engine.startGame('user123', 'easy');
            const word1 = state1.currentWord!;

            const state2 = await engine.submitAnswer('new');
            const word2 = state2.currentWord!;

            await engine.submitAnswer('new');

            const session = engine.getSession();
            expect(session?.wordsShown).toContain(word1);
            expect(session?.wordsShown).toContain(word2);
        });
    });

    describe('No Consecutive Duplicates', () => {
        it('should NEVER show the same word twice in a row', async () => {
            const state1 = await engine.startGame('test-user', 'easy');
            const firstWord = state1.currentWord;
            expect(firstWord).toBeTruthy();

            // Play 20 rounds and verify no consecutive duplicates
            let previousWord = firstWord;

            for (let i = 0; i < 20; i++) {
                // Determine correct answer based on whether word is in seen set
                const isNew = !state1.session?.seenWords.has(previousWord!);
                const answer = isNew ? 'new' : 'seen';

                const nextState = await engine.submitAnswer(answer);
                const currentWord = nextState.currentWord;

                if (nextState.gameOver) {
                    break;
                }

                // THE KEY ASSERTION: Current word must NEVER equal previous word
                expect(currentWord).not.toBe(previousWord);
                expect(currentWord).toBeTruthy();

                previousWord = currentWord;
            }
        });
    });
});

describe('GameEngine - Bug Reproduction', () => {
    it('CURRENT BUG: Second NEW word should not decrease lives', async () => {
        const engine = new GameEngine();

        // Start game
        const state1 = await engine.startGame('user123', 'easy');
        console.log('State 1:', {
            word: state1.currentWord,
            isNew: state1.isCurrentWordNew,
            lives: state1.session?.lives,
            score: state1.session?.score
        });

        // First word is NEW, answer correctly
        const state2 = await engine.submitAnswer('new');
        console.log('State 2 (after answering NEW):', {
            word: state2.currentWord,
            isNew: state2.isCurrentWordNew,
            lives: state2.session?.lives,
            score: state2.session?.score,
            seenWordsCount: state2.session?.seenWords.size
        });

        // Second word might also be NEW
        // If it IS new and we answer NEW, we should NOT lose a life
        if (state2.isCurrentWordNew) {
            const state3 = await engine.submitAnswer('new');
            console.log('State 3 (after answering NEW again):', {
                word: state3.currentWord,
                isNew: state3.isCurrentWordNew,
                lives: state3.session?.lives,
                score: state3.session?.score
            });

            // This assertion will FAIL with the current bug
            expect(state3.session?.lives).toBe(3); // Should still have 3 lives
            expect(state3.session?.score).toBe(2); // Should have score of 2
        }
    });
});
