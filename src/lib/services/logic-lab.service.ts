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
	age: number;
	guidance?: string;
}

export interface SubmitAnswerResult {
	correct: boolean;
	explanation: string;
	nextProblem?: {
		question: string;
		options: string[];
		type?: string;
		difficulty?: number;
		inputTokens?: number;
	};
	score: number;
	lives: number;
	round: number;
	gameOver: boolean;
	finalScore?: number;
	difficultyLevel?: number;
	consecutiveCorrect?: number;
	consecutiveIncorrect?: number;
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
		// Try to load existing Logic Lab session for this user
		const existingSession = await this.repository.findActiveLogicLabSession(params.userId);

		if (existingSession && existingSession.logicLabState) {
			// Resume existing game
			const state = existingSession.logicLabState;

			// Update age/guidance if changed
			state.age = params.age;
			state.guidance = params.guidance || '';
			state.lastPlayedAt = new Date();

			// Generate next problem
			const nextProblem = await this.generateNextProblem(existingSession);
			state.currentProblem = nextProblem;
			state.problemHistory.push(nextProblem);

			existingSession.round += 1;

			await this.repository.update(existingSession._id!, existingSession);
			return existingSession;
		}

		// Create new Logic Lab state
		const initialDifficultyLevel = this.mapAgeToLevel(params.age);

		const firstProblem = await this.generateFirstProblem({
			age: params.age,
			guidance: params.guidance,
			difficultyLevel: initialDifficultyLevel
		});

		const gameSession: GameSession = {
			userId: params.userId,
			gameType: 'logic-lab',
			difficulty: 'easy', // Deprecated, but keep for compatibility
			score: 0,
			lives: 999, // Infinite lives
			round: 1,
			logicLabState: {
				age: params.age,
				guidance: params.guidance || '',
				modelName: 'google/gemini-2.5-flash',
				currentProblem: firstProblem,
				problemHistory: [firstProblem],
				correctAnswers: 0,
				consecutiveCorrect: 0,
				consecutiveIncorrect: 0,
				currentDifficultyLevel: initialDifficultyLevel,
				hintsUsed: 0,
				lastPlayedAt: new Date()
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

		// Move to next round (infinite mode - no game over!)
		session.round += 1;

		// Calculate next difficulty
		const nextDifficulty = this.calculateNextDifficulty(session);
		session.logicLabState.currentDifficultyLevel = nextDifficulty;

		// Generate next problem
		const nextProblem = await this.generateNextProblem(session);
		session.logicLabState.currentProblem = nextProblem;
		session.logicLabState.problemHistory.push(nextProblem);

		// Save session
		await this.repository.update(sessionId, session);

		return {
			correct: isCorrect,
			explanation: session.logicLabState.problemHistory[session.logicLabState.problemHistory.length - 2].explanation,
			nextProblem: {
				question: nextProblem.question,
				options: nextProblem.options,
				type: nextProblem.type,
				difficulty: nextProblem.difficultyLevel,
				inputTokens: nextProblem.inputTokens
			},
			score: session.score,
			lives: session.lives,
			round: session.round,
			gameOver: false, // Never game over!
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

	async resetProgress(userId: string): Promise<void> {
		// Find and mark the user's Logic Lab session as inactive
		const existingSession = await this.repository.findActiveLogicLabSession(userId);
		if (existingSession && existingSession._id) {
			await this.repository.update(existingSession._id, {
				isActive: false,
				endedAt: new Date()
			});
		}
	}

	// Private helper methods

	private async generateFirstProblem(params: {
		age: number;
		guidance?: string;
		difficultyLevel: number;
	}): Promise<Problem> {
		const problemType = this.selectProblemType([]);
		const age = params.age;

		const llmParams: GenerateProblemParams = {
			initialGuidance: params.guidance || '',
			age,
			difficulty: 'easy', // Not used anymore
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
		const age = state.age;

		// Select problem type (avoid last type)
		const previousTypes = state.problemHistory.map((p) => p.type);
		const problemType = this.selectProblemType(previousTypes);

		// Build performance history for LLM (ALL problems with answers to avoid any repetition)
		const performanceHistory = state.problemHistory
			.filter((p) => p.userAnswerIndex !== undefined)
			.map((p) => ({
				question: p.question,
				type: p.type,
				difficulty: p.difficultyLevel,
				correct: p.isCorrect || false,
				theme: p.theme // Include theme for better tracking
			}));

		const llmParams: GenerateProblemParams = {
			initialGuidance: state.guidance,
			age,
			difficulty: 'easy', // Not used anymore
			difficultyLevel: state.currentDifficultyLevel,
			problemType,
			performanceHistory,
			consecutiveCorrect: state.consecutiveCorrect,
			consecutiveIncorrect: state.consecutiveIncorrect
		};

		// Retry logic: Try up to 3 times to get a unique question
		const maxRetries = 3;
		const recentQuestions = state.problemHistory.slice(-10).map((p) => p.question);

		for (let attempt = 1; attempt <= maxRetries; attempt++) {
			const problem = await this.llmService.generateProblem(llmParams);

			// Check if question is too similar to recent questions
			const isSimilar = this.isSimilarToRecent(problem.question, recentQuestions);

			if (!isSimilar) {
				// Question is unique, return it
				return problem;
			}

			// If this was the last attempt, return it anyway (better than blocking)
			if (attempt === maxRetries) {
				console.warn(`Failed to generate unique question after ${maxRetries} attempts, using last attempt`);
				return problem;
			}

			// Otherwise, retry
			console.log(`Attempt ${attempt}: Question too similar, retrying...`);
		}

		// This should never be reached, but TypeScript needs it
		throw new Error('Failed to generate problem');
	}

	private selectProblemType(previousTypes: ProblemType[]): ProblemType {
		// Avoid last 2-3 types to ensure better variety
		const recentCount = Math.min(2, previousTypes.length);
		const recentTypes = new Set(previousTypes.slice(-recentCount));

		// Filter out recent types
		const availableTypes = PROBLEM_TYPES.filter((t) => !recentTypes.has(t));

		// If we've filtered out too many, fall back to excluding only the last type
		if (availableTypes.length === 0) {
			const lastType = previousTypes[previousTypes.length - 1];
			const fallbackTypes = PROBLEM_TYPES.filter((t) => t !== lastType);

			if (fallbackTypes.length > 0) {
				return fallbackTypes[Math.floor(Math.random() * fallbackTypes.length)];
			}

			// Last resort: any random type
			return PROBLEM_TYPES[Math.floor(Math.random() * PROBLEM_TYPES.length)];
		}

		return availableTypes[Math.floor(Math.random() * availableTypes.length)];
	}

	/**
	 * Check if a new question is too similar to recent questions
	 * @param newQuestion - The newly generated question
	 * @param recentQuestions - Array of recent question strings to compare against
	 * @param threshold - Similarity threshold (0-1), default 0.6 (60% word overlap)
	 * @returns true if the question is too similar, false otherwise
	 */
	private isSimilarToRecent(
		newQuestion: string,
		recentQuestions: string[],
		threshold: number = 0.6
	): boolean {
		// Check last 10 questions max
		const questionsToCheck = recentQuestions.slice(-10);

		// Normalize and tokenize the new question
		const newWords = new Set(
			newQuestion
				.toLowerCase()
				.replace(/[?.,!]/g, '')
				.split(/\s+/)
				.filter((w) => w.length > 2) // Ignore very short words
		);

		for (const oldQ of questionsToCheck) {
			// Normalize and tokenize the old question
			const oldWords = new Set(
				oldQ
					.toLowerCase()
					.replace(/[?.,!]/g, '')
					.split(/\s+/)
					.filter((w) => w.length > 2)
			);

			// Calculate word overlap
			const overlap = [...newWords].filter((w) => oldWords.has(w)).length;
			const maxSize = Math.max(newWords.size, oldWords.size);

			if (maxSize === 0) continue; // Avoid division by zero

			const similarity = overlap / maxSize;

			// If similarity is above threshold, consider it too similar
			if (similarity > threshold) {
				console.warn(`Question too similar to recent question (${Math.round(similarity * 100)}% overlap)`);
				console.warn(`New: "${newQuestion}"`);
				console.warn(`Old: "${oldQ}"`);
				return true;
			}
		}

		return false;
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
			nextLevel = Math.max(2, nextLevel - 1); // Floor at 2, not 1 (1 is too easy)
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

	private mapAgeToLevel(age: number): number {
		// Start at level 3 for younger kids, level 4 for older
		// Age 4-6: Level 3
		// Age 7+: Level 4
		return age >= 7 ? 4 : 3;
	}
}
