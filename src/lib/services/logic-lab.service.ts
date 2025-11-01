import type {
	GameSession,
	DifficultyLevel,
	Problem,
	ProblemType,
	LogicLabGameState
} from '$lib/types';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';
import { LLMService, type GenerateProblemParams } from './llm.service';

export interface StartGameParams {
	userId: string;
	difficulty: DifficultyLevel;
	initialGuidance?: string;
}

export interface SubmitAnswerResult {
	correct: boolean;
	explanation: string;
	nextProblem?: {
		question: string;
		options: string[];
	};
	score: number;
	lives: number;
	round: number;
	gameOver: boolean;
	finalScore?: number;
}

const PROBLEM_TYPES: ProblemType[] = ['pattern', 'category', 'comparison', 'grouping'];

export class LogicLabEngine {
	private repository: GameSessionRepository;
	private llmService: LLMService;

	constructor() {
		this.repository = new GameSessionRepository();
		this.llmService = new LLMService();
	}

	async startGame(params: StartGameParams): Promise<GameSession> {
		const initialDifficultyLevel = this.mapDifficultyToLevel(params.difficulty);

		// Generate first problem
		const firstProblem = await this.generateFirstProblem({
			initialGuidance: params.initialGuidance,
			difficulty: params.difficulty,
			difficultyLevel: initialDifficultyLevel
		});

		// Create game session
		const gameSession: GameSession = {
			userId: params.userId,
			gameType: 'logic-lab',
			difficulty: params.difficulty,
			score: 0,
			lives: 3,
			round: 1,
			logicLabState: {
				initialGuidance: params.initialGuidance || '',
				modelName: 'google/gemini-2.5-flash',
				currentProblem: firstProblem,
				problemHistory: [firstProblem],
				correctAnswers: 0,
				consecutiveCorrect: 0,
				consecutiveIncorrect: 0,
				currentDifficultyLevel: initialDifficultyLevel,
				totalProblems: 15,
				hintsUsed: 0
			},
			isActive: true,
			startedAt: new Date()
		};

		return await this.repository.create(gameSession);
	}

	async submitAnswer(sessionId: string, answerIndex: number): Promise<SubmitAnswerResult | null> {
		// Load game session
		const session = await this.repository.findById(sessionId);
		if (!session || !session.logicLabState) {
			return null;
		}

		const startTime = Date.now();

		// Evaluate answer
		const isCorrect = this.evaluateAnswer(session, answerIndex);

		// Record answer in problem
		session.logicLabState.currentProblem.userAnswerIndex = answerIndex;
		session.logicLabState.currentProblem.isCorrect = isCorrect;
		session.logicLabState.currentProblem.responseTime = Date.now() - startTime;

		// Update score and lives
		this.updateScore(session, isCorrect);

		// Check if game is over
		const gameOver = this.isGameOver(session);

		let nextProblem: Problem | null = null;

		if (!gameOver) {
			// Move to next round
			session.round += 1;

			// Calculate next difficulty
			const nextDifficulty = this.calculateNextDifficulty(session);
			session.logicLabState.currentDifficultyLevel = nextDifficulty;

			// Generate next problem
			nextProblem = await this.generateNextProblem(session);
			session.logicLabState.currentProblem = nextProblem;
			session.logicLabState.problemHistory.push(nextProblem);
		} else {
			session.isActive = false;
			session.endedAt = new Date();
		}

		// Save session
		await this.repository.update(sessionId, session);

		return {
			correct: isCorrect,
			explanation: session.logicLabState.problemHistory[session.logicLabState.problemHistory.length - 1 - (gameOver ? 0 : 1)].explanation,
			nextProblem: nextProblem
				? {
						question: nextProblem.question,
						options: nextProblem.options,
						type: nextProblem.type,
						difficulty: nextProblem.difficultyLevel
					}
				: undefined,
			score: session.score,
			lives: session.lives,
			round: session.round,
			gameOver,
			finalScore: gameOver ? session.score : undefined,
			// Debug info for parents
			difficultyLevel: session.logicLabState.currentDifficultyLevel,
			consecutiveCorrect: session.logicLabState.consecutiveCorrect,
			consecutiveIncorrect: session.logicLabState.consecutiveIncorrect
		};
	}

	async getStats(sessionId: string): Promise<any> {
		const session = await this.repository.findById(sessionId);
		if (!session || !session.logicLabState) {
			return null;
		}

		return {
			sessionId,
			score: session.score,
			lives: session.lives,
			totalProblems: session.logicLabState.totalProblems,
			correctAnswers: session.logicLabState.correctAnswers,
			problemHistory: session.logicLabState.problemHistory.map((p) => ({
				question: p.question,
				type: p.type,
				userAnswer: p.userAnswerIndex !== undefined ? p.options[p.userAnswerIndex] : null,
				correctAnswer: p.options[p.correctIndex],
				isCorrect: p.isCorrect
			})),
			startedAt: session.startedAt,
			endedAt: session.endedAt
		};
	}

	// Private helper methods

	private async generateFirstProblem(params: {
		initialGuidance?: string;
		difficulty: DifficultyLevel;
		difficultyLevel: number;
	}): Promise<Problem> {
		const problemType = this.selectProblemType([]);
		const age = params.difficulty === 'easy' ? 6 : 8;

		const llmParams: GenerateProblemParams = {
			initialGuidance: params.initialGuidance,
			age,
			difficulty: params.difficulty,
			difficultyLevel: params.difficultyLevel,
			problemType,
			performanceHistory: [],
			consecutiveCorrect: 0,
			consecutiveIncorrect: 0
		};

		return await this.llmService.generateProblem(llmParams);
	}

	private async generateNextProblem(session: GameSession): Promise<Problem> {
		const state = session.logicLabState!;
		const age = session.difficulty === 'easy' ? 6 : 8;

		// Select problem type (avoid last type)
		const previousTypes = state.problemHistory.map((p) => p.type);
		const problemType = this.selectProblemType(previousTypes);

		// Build performance history for LLM (last 5 problems with answers)
		const performanceHistory = state.problemHistory
			.filter((p) => p.userAnswerIndex !== undefined)
			.slice(-5)
			.map((p) => ({
				question: p.question,
				type: p.type,
				difficulty: p.difficultyLevel,
				correct: p.isCorrect || false
			}));

		const llmParams: GenerateProblemParams = {
			initialGuidance: state.initialGuidance,
			age,
			difficulty: session.difficulty,
			difficultyLevel: state.currentDifficultyLevel, // Pass the calculated difficulty level!
			problemType,
			performanceHistory,
			consecutiveCorrect: state.consecutiveCorrect,
			consecutiveIncorrect: state.consecutiveIncorrect
		};

		return await this.llmService.generateProblem(llmParams);
	}

	private selectProblemType(previousTypes: ProblemType[]): ProblemType {
		const lastType = previousTypes[previousTypes.length - 1];
		const availableTypes = PROBLEM_TYPES.filter((t) => t !== lastType);

		if (availableTypes.length === 0) {
			return PROBLEM_TYPES[Math.floor(Math.random() * PROBLEM_TYPES.length)];
		}

		return availableTypes[Math.floor(Math.random() * availableTypes.length)];
	}

	private calculateNextDifficulty(session: GameSession): number {
		const state = session.logicLabState!;
		let nextLevel = state.currentDifficultyLevel;

		// Increase difficulty after 2 correct in a row
		if (state.consecutiveCorrect >= 2) {
			nextLevel = Math.min(5, nextLevel + 1);
		}

		// Decrease difficulty after 2 incorrect in a row
		if (state.consecutiveIncorrect >= 2) {
			nextLevel = Math.max(1, nextLevel - 1);
		}

		return nextLevel;
	}

	private evaluateAnswer(session: GameSession, answerIndex: number): boolean {
		const state = session.logicLabState!;
		return state.currentProblem.correctIndex === answerIndex;
	}

	private updateScore(session: GameSession, isCorrect: boolean): void {
		const state = session.logicLabState!;

		if (isCorrect) {
			session.score += 1;
			state.correctAnswers += 1;
			state.consecutiveCorrect += 1;
			state.consecutiveIncorrect = 0;
		} else {
			session.lives -= 1;
			state.consecutiveCorrect = 0;
			state.consecutiveIncorrect += 1;
		}
	}

	private isGameOver(session: GameSession): boolean {
		const state = session.logicLabState!;
		return session.lives <= 0 || session.round >= state.totalProblems;
	}

	private mapDifficultyToLevel(difficulty: DifficultyLevel): number {
		return difficulty === 'easy' ? 2 : 3;
	}
}
