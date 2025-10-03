import { describe, it, expect, beforeEach } from 'vitest';
import { WordService } from './word.service';

describe('WordService', () => {
    let easyService: WordService;
    let hardService: WordService;

    beforeEach(() => {
        easyService = new WordService('easy');
        hardService = new WordService('hard');
    });

    describe('constructor and initialization', () => {
        it('should initialize with easy difficulty word pool', () => {
            const words = easyService.getWordPool();
            expect(words).toBeDefined();
            expect(words.length).toBeGreaterThan(0);
            // Easy words should be simpler (checking a few known easy words)
            expect(words).toContain('Hund');
            expect(words).toContain('Katze');
        });

        it('should initialize with hard difficulty word pool', () => {
            const words = hardService.getWordPool();
            expect(words).toBeDefined();
            expect(words.length).toBeGreaterThan(0);
            // Hard words should be more complex
            expect(words.some(word => word.length > 6)).toBe(true);
        });

        it('should reset word pool on reset()', () => {
            const pool1 = easyService.getWordPool();
            easyService.reset();
            const pool2 = easyService.getWordPool();
            expect(pool1).toEqual(pool2);
        });
    });

    describe('getRandomWord', () => {
        it('should return a word from the pool', () => {
            const word = easyService.getRandomWord(new Set());
            const pool = easyService.getWordPool();
            expect(pool).toContain(word);
        });

        it('should not return a word from excluded set', () => {
            const pool = easyService.getWordPool();
            const excludedWords = new Set([pool[0], pool[1], pool[2]]);
            
            // Get 10 words and ensure none are in excluded set
            for (let i = 0; i < 10; i++) {
                const word = easyService.getRandomWord(excludedWords);
                expect(excludedWords.has(word)).toBe(false);
            }
        });

        it('should return different words on consecutive calls (high probability)', () => {
            const word1 = easyService.getRandomWord(new Set());
            const word2 = easyService.getRandomWord(new Set([word1]));
            expect(word2).not.toBe(word1);
        });

        it('should handle excluding most words and still return available word', () => {
            const pool = easyService.getWordPool();
            // Exclude all but 2 words
            const excludedWords = new Set(pool.slice(0, pool.length - 2));
            
            const word = easyService.getRandomWord(excludedWords);
            expect(excludedWords.has(word)).toBe(false);
            expect(pool).toContain(word);
        });

        it('should throw error when no words available', () => {
            const pool = easyService.getWordPool();
            const allWords = new Set(pool);
            
            expect(() => {
                easyService.getRandomWord(allWords);
            }).toThrow('No more words available in the pool');
        });
    });

    describe('getRandomSeenWord', () => {
        it('should return a word from seen words', () => {
            const seenWords = new Set(['Hund', 'Katze', 'Maus']);
            const word = easyService.getRandomSeenWord(seenWords);
            expect(seenWords.has(word)).toBe(true);
        });

        it('should not return the excluded word', () => {
            const seenWords = new Set(['Hund', 'Katze', 'Maus']);
            const excludeWord = 'Hund';
            
            // Get multiple words to ensure exclusion works
            for (let i = 0; i < 10; i++) {
                const word = easyService.getRandomSeenWord(seenWords, excludeWord);
                expect(word).not.toBe(excludeWord);
                expect(['Katze', 'Maus']).toContain(word);
            }
        });

        it('should return word when excludeWord is null', () => {
            const seenWords = new Set(['Hund', 'Katze', 'Maus']);
            const word = easyService.getRandomSeenWord(seenWords, null);
            expect(seenWords.has(word)).toBe(true);
        });

        it('should return word when excludeWord is not in seen words', () => {
            const seenWords = new Set(['Hund', 'Katze', 'Maus']);
            const excludeWord = 'Vogel'; // Not in seenWords
            const word = easyService.getRandomSeenWord(seenWords, excludeWord);
            expect(seenWords.has(word)).toBe(true);
        });

        it('should throw error when no seen words available', () => {
            const seenWords = new Set<string>();
            
            expect(() => {
                easyService.getRandomSeenWord(seenWords);
            }).toThrow('No seen words available');
        });

        it('should throw error when only seen word is the excluded word', () => {
            const seenWords = new Set(['Hund']);
            const excludeWord = 'Hund';
            
            expect(() => {
                easyService.getRandomSeenWord(seenWords, excludeWord);
            }).toThrow('No seen words available');
        });
    });

    describe('shouldShowNewWord', () => {
        it('should return a boolean', () => {
            const result = easyService.shouldShowNewWord();
            expect(typeof result).toBe('boolean');
        });

        it('should return true approximately 50% of the time', () => {
            const iterations = 1000;
            let trueCount = 0;

            for (let i = 0; i < iterations; i++) {
                if (easyService.shouldShowNewWord()) {
                    trueCount++;
                }
            }

            // Should be close to 50% (allow 40-60% range for randomness)
            const percentage = (trueCount / iterations) * 100;
            expect(percentage).toBeGreaterThan(40);
            expect(percentage).toBeLessThan(60);
        });
    });

    describe('no consecutive duplicates', () => {
        it('should not return same word twice in a row when using exclusion', () => {
            const iterations = 20;
            let previousWord = easyService.getRandomWord(new Set());

            for (let i = 0; i < iterations; i++) {
                // Exclude the previous word
                const currentWord = easyService.getRandomWord(new Set([previousWord]));
                expect(currentWord).not.toBe(previousWord);
                previousWord = currentWord;
            }
        });

        it('should not return same seen word twice in a row when using exclusion', () => {
            const seenWords = new Set(['Hund', 'Katze', 'Maus', 'Vogel', 'Fisch']);
            const iterations = 20;
            let previousWord = easyService.getRandomSeenWord(seenWords);

            for (let i = 0; i < iterations; i++) {
                const currentWord = easyService.getRandomSeenWord(seenWords, previousWord);
                expect(currentWord).not.toBe(previousWord);
                previousWord = currentWord;
            }
        });
    });

    describe('difficulty-specific behavior', () => {
        it('easy and hard pools should be different', () => {
            const easyPool = easyService.getWordPool();
            const hardPool = hardService.getWordPool();
            
            // Pools should have different contents
            const easySet = new Set(easyPool);
            const hardSet = new Set(hardPool);
            
            // Not all words should be the same
            const intersection = new Set([...easySet].filter(x => hardSet.has(x)));
            expect(intersection.size).toBeLessThan(Math.min(easyPool.length, hardPool.length));
        });

        it('should maintain separate word pools for different difficulties', () => {
            const easyWord = easyService.getRandomWord(new Set());
            const hardWord = hardService.getRandomWord(new Set());
            
            const easyPool = easyService.getWordPool();
            const hardPool = hardService.getWordPool();
            
            expect(easyPool).toContain(easyWord);
            expect(hardPool).toContain(hardWord);
        });
    });
});

