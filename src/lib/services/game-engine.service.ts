import type { GameSession, DifficultyLevel } from '$lib/types';
import { WordService } from './word.service';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';

export interface GameAction {
    type: 'start' | 'answer' | 'end';
    payload?: {
        userId?: string;
        difficulty?: DifficultyLevel;
        answer?: 'seen' | 'new';
    };
}

export interface GameState {
    session: GameSession | null;
    currentWord: string | null;
    isCurrentWordNew: boolean;
    isCorrect: boolean | null;
    gameOver: boolean;
    message: string | null;
}

export class GameEngine {
    private wordService: WordService;
    private repository: GameSessionRepository;
    private session: GameSession | null = null;
    private currentWord: string | null = null;
    private isCurrentWordNew: boolean = false;

    constructor() {
        this.wordService = new WordService('easy');
        this.repository = new GameSessionRepository();
    }

    async startGame(userId: string, difficulty: DifficultyLevel): Promise<GameState> {
        this.wordService = new WordService(difficulty);

        this.session = await this.repository.create({
            userId,
            gameType: 'verbal-memory',
            difficulty,
            score: 0,
            lives: 3,
            round: 0,
            wordsShown: [],
            seenWords: new Set(),
            currentWord: null,
            previousWord: null,
            isCurrentWordNew: false,
            isActive: true,
            startedAt: new Date()
        });

        return this.nextWord();
    }

    async loadGame(sessionId: string): Promise<void> {
        this.session = await this.repository.findById(sessionId);

        if (!this.session) {
            throw new Error('Game session not found');
        }

        this.wordService = new WordService(this.session.difficulty);
        // Restore the current word state from the session
        this.currentWord = this.session.currentWord;
        this.isCurrentWordNew = this.session.isCurrentWordNew;
    }

    private async nextWord(): Promise<GameState> {
        if (!this.session || !this.session.isActive) {
            return this.createGameState(null, false, null, true, 'Game is not active');
        }

        // Increment round counter
        this.session.round++;

        // The word we need to avoid showing again is the CURRENT word (the one just shown)
        // NOT session.previousWord (which is the word from 2 rounds ago)
        const wordToAvoid = this.session.currentWord;

        // Check if we can show an old word that's different from the word to avoid
        const canShowOldWord = this.session.seenWords.size > 0;
        let canShowDifferentOldWord = false;
        
        if (canShowOldWord && wordToAvoid) {
            // Can we show a seen word that's NOT the word to avoid?
            canShowDifferentOldWord = Array.from(this.session.seenWords).some(
                word => word !== wordToAvoid
            );
        } else if (canShowOldWord) {
            // No word to avoid
            canShowDifferentOldWord = true;
        }

        // Create exclusion set: exclude previously seen words AND the word to avoid
        const excludeWords = new Set(this.session.seenWords);
        if (wordToAvoid) {
            excludeWords.add(wordToAvoid);
        }

        // Decide: show NEW or OLD word
        // Show NEW if: no old words available, can't show different old word, or randomly decided
        const shouldShowNew = !canShowOldWord || !canShowDifferentOldWord || this.wordService.shouldShowNewWord();
        
        if (shouldShowNew) {
            // Get a NEW word (not in seen words, and not the previous word)
            this.currentWord = this.wordService.getRandomWord(excludeWords);
            this.isCurrentWordNew = true;
        } else {
            // Show an OLD word (from seen words, but not the word to avoid)
            this.currentWord = this.wordService.getRandomSeenWord(
                this.session.seenWords,
                wordToAvoid
            );
            this.isCurrentWordNew = false;
        }

        // Save the CURRENT word as the previous word for NEXT round
        // (but only if currentWord is not null - on first round it's null)
        const newPreviousWord = this.session.currentWord;
        
        // Update session with new word
        this.session.currentWord = this.currentWord;
        this.session.previousWord = newPreviousWord;
        this.session.isCurrentWordNew = this.isCurrentWordNew;

        await this.repository.update(this.session._id!, {
            round: this.session.round,
            currentWord: this.currentWord,
            previousWord: newPreviousWord,
            isCurrentWordNew: this.isCurrentWordNew
        });

        return this.createGameState(this.currentWord, this.isCurrentWordNew, null, false, null);
    }

    async submitAnswer(answer: 'seen' | 'new'): Promise<GameState> {
        if (!this.session || !this.currentWord) {
            throw new Error('No active game or word');
        }

        const isCorrect = (answer === 'new' && this.isCurrentWordNew) ||
            (answer === 'seen' && !this.isCurrentWordNew);

        if (isCorrect) {
            this.session.score++;

            if (this.isCurrentWordNew) {
                this.session.seenWords.add(this.currentWord);
            }
        } else {
            this.session.lives--;
        }

        this.session.wordsShown.push(this.currentWord);

        // FIXED: Don't let lives go negative
        if (this.session.lives < 0) {
            this.session.lives = 0;
        }

        await this.repository.update(this.session._id!, {
            score: this.session.score,
            lives: this.session.lives,
            wordsShown: this.session.wordsShown,
            seenWords: this.session.seenWords
        });

        if (this.session.lives <= 0) {
            return await this.endGame();
        }

        return this.nextWord();
    }

    async endGame(): Promise<GameState> {
        if (!this.session) {
            throw new Error('No active game');
        }

        this.session.isActive = false;
        this.session.endedAt = new Date();

        await this.repository.update(this.session._id!, {
            isActive: false,
            endedAt: this.session.endedAt
        });

        return this.createGameState(
            null,
            false,
            null,
            true,
            `Spiel vorbei! Deine Punktzahl: ${this.session.score}`
        );
    }

    private createGameState(
        currentWord: string | null,
        isCurrentWordNew: boolean,
        isCorrect: boolean | null,
        gameOver: boolean,
        message: string | null
    ): GameState {
        return {
            session: this.session,
            currentWord,
            isCurrentWordNew,
            isCorrect,
            gameOver,
            message
        };
    }

    getSession(): GameSession | null {
        return this.session;
    }
}
