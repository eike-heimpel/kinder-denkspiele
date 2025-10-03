import type { DifficultyLevel } from '$lib/types';
import { germanWordPools } from '$lib/data/word-pools';

export class WordService {
    private usedWords: Set<string> = new Set();

    constructor(private difficulty: DifficultyLevel) { }

    getWordPool(): string[] {
        return this.difficulty === 'easy' ? germanWordPools.easy : germanWordPools.hard;
    }

    getRandomWord(excludeWords: Set<string> = new Set()): string {
        const pool = this.getWordPool();
        const availableWords = pool.filter(word => !excludeWords.has(word));

        if (availableWords.length === 0) {
            throw new Error('No more words available in the pool');
        }

        const randomIndex = Math.floor(Math.random() * availableWords.length);
        return availableWords[randomIndex];
    }

    getRandomSeenWord(seenWords: Set<string>): string {
        const seenArray = Array.from(seenWords);
        if (seenArray.length === 0) {
            throw new Error('No seen words available');
        }

        const randomIndex = Math.floor(Math.random() * seenArray.length);
        return seenArray[randomIndex];
    }

    shouldShowNewWord(): boolean {
        return Math.random() < 0.5;
    }

    reset(): void {
        this.usedWords.clear();
    }
}
