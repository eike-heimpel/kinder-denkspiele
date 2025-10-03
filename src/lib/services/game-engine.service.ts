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
            wordsShown: [],
            seenWords: new Set(),
            isActive: true,
            startedAt: new Date()
        });

        return this.nextWord();
    }

    async loadGame(sessionId: string): Promise<GameState> {
        this.session = await this.repository.findById(sessionId);

        if (!this.session) {
            throw new Error('Game session not found');
        }

        this.wordService = new WordService(this.session.difficulty);
        return this.nextWord();
    }

    private nextWord(): GameState {
        if (!this.session || !this.session.isActive) {
            return this.createGameState(null, false, null, true, 'Game is not active');
        }

        const canShowOldWord = this.session.seenWords.size > 0;

        if (canShowOldWord && this.wordService.shouldShowNewWord()) {
            this.currentWord = this.wordService.getRandomSeenWord(this.session.seenWords);
            this.isCurrentWordNew = false;
        } else {
            this.currentWord = this.wordService.getRandomWord(this.session.seenWords);
            this.isCurrentWordNew = true;
        }

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
