import { OPENROUTER_API_KEY } from '$env/static/private';
import { PromptLoader, type RenderedPrompt } from './prompt-loader.service';
import { encoding_for_model } from 'tiktoken';

export interface GenerateProblemParams {
	initialGuidance?: string;
	age: number;
	difficulty: 'easy' | 'hard';
	difficultyLevel: number; // 1-5 target difficulty
	problemType: 'pattern' | 'category' | 'comparison' | 'grouping';
	performanceHistory: Array<{
		question: string;
		type: string;
		difficulty: number;
		correct: boolean;
		theme?: string;
	}>;
	consecutiveCorrect: number;
	consecutiveIncorrect: number;
}

export interface Problem {
	id: string;
	type: 'pattern' | 'category' | 'comparison' | 'grouping';
	question: string;
	options: string[];
	correctIndex: number;
	explanation: string;
	difficultyLevel: number;
	theme?: string;
	inputTokens?: number; // Number of tokens sent to LLM
	timestamp: Date;
	userAnswerIndex?: number;
	isCorrect?: boolean;
	responseTime?: number;
}

interface OpenRouterResponse {
	choices: Array<{
		message: {
			role: string;
			content: string;
		};
		finish_reason: string;
	}>;
	usage: {
		prompt_tokens: number;
		completion_tokens: number;
		total_tokens: number;
	};
}

// Fallback problems if LLM fails
const FALLBACK_PROBLEMS: Array<Omit<Problem, 'id' | 'timestamp'>> = [
	{
		type: 'category',
		question: 'Welches passt NICHT zu den anderen?',
		options: ['Hund', 'Katze', 'Baum', 'Vogel'],
		correctIndex: 2,
		explanation: 'Der Baum ist eine Pflanze, die anderen sind Tiere!',
		difficultyLevel: 1
	},
	{
		type: 'pattern',
		question: 'Welche Zahl kommt als nächstes? 2, 4, 6, ___',
		options: ['8', '7', '5', '10'],
		correctIndex: 0,
		explanation: 'Die Zahlen zählen in 2er-Schritten: 2, 4, 6, 8!',
		difficultyLevel: 2
	},
	{
		type: 'comparison',
		question: 'Welches Tier kann fliegen?',
		options: ['Hund', 'Katze', 'Vogel', 'Fisch'],
		correctIndex: 2,
		explanation: 'Der Vogel hat Flügel und kann fliegen!',
		difficultyLevel: 1
	},
	{
		type: 'grouping',
		question: 'Was haben Apfel, Banane und Orange gemeinsam?',
		options: ['Sie sind alle rot', 'Sie sind alle Obst', 'Sie sind alle grün', 'Sie sind alle Gemüse'],
		correctIndex: 1,
		explanation: 'Apfel, Banane und Orange sind alles Obst!',
		difficultyLevel: 2
	},
	{
		type: 'category',
		question: 'Welche Farbe passt NICHT zu den anderen?',
		options: ['Rot', 'Blau', 'Hund', 'Grün'],
		correctIndex: 2,
		explanation: 'Hund ist ein Tier, die anderen sind Farben!',
		difficultyLevel: 1
	}
];

const BANNED_WORDS = [
	'tot',
	'sterben',
	'gewalt',
	'blut',
	'waffe',
	'krieg',
	'terror',
	'mord',
	'töten',
	'schießen'
];

export class LLMService {
	private apiKey: string;
	private baseUrl: string = 'https://openrouter.ai/api/v1';
	private promptLoader: PromptLoader;

	constructor() {
		if (!OPENROUTER_API_KEY) {
			throw new Error('OPENROUTER_API_KEY environment variable is not set');
		}
		this.apiKey = OPENROUTER_API_KEY;
		this.promptLoader = new PromptLoader();
	}

	async generateProblem(params: GenerateProblemParams): Promise<Problem> {
		try {
			// Render prompt using YAML template
			const rendered = this.promptLoader.renderPrompt('generate-problem', {
				initial_guidance: params.initialGuidance,
				age: params.age,
				difficulty: params.difficulty,
				difficulty_level: params.difficultyLevel,
				problem_type: params.problemType,
				performance_history: params.performanceHistory,
				consecutive_correct: params.consecutiveCorrect,
				consecutive_incorrect: params.consecutiveIncorrect
			});

			// Count input tokens
			const inputTokens = this.countTokens(rendered.system_prompt, rendered.user_prompt);

			// Call OpenRouter API to generate problem
			const response = await this.callOpenRouter(rendered);

			// Parse and validate response
			const problem = this.parseResponse(response);

			// Add token count to problem
			problem.inputTokens = inputTokens;

			if (!this.validateProblem(problem)) {
				console.error('Generated problem failed basic validation');
				return this.getFallbackProblem(2);
			}

			// Second validation: Check logical consistency with LLM
			const isLogicallyValid = await this.validateProblemLogic(problem, params.age);
			if (!isLogicallyValid) {
				console.error('Generated problem failed logical validation, using fallback');
				return this.getFallbackProblem(2);
			}

			return problem;
		} catch (error) {
			console.error('LLM generation failed:', error);
			return this.getFallbackProblem(2);
		}
	}

	private async callOpenRouter(rendered: RenderedPrompt): Promise<string> {
		const response = await fetch(`${this.baseUrl}/chat/completions`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${this.apiKey}`,
				'Content-Type': 'application/json',
				'HTTP-Referer': 'https://localhost:5173',
				'X-Title': 'Kinder Denkspiele'
			},
			body: JSON.stringify({
				model: rendered.model,
				temperature: rendered.temperature,
				max_tokens: rendered.max_tokens,
				response_format: rendered.response_format,
				messages: [
					{ role: 'system', content: rendered.system_prompt },
					{ role: 'user', content: rendered.user_prompt }
				]
			})
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`OpenRouter API error (${response.status}): ${errorText}`);
		}

		const data: OpenRouterResponse = await response.json();

		if (!data.choices || data.choices.length === 0) {
			throw new Error('No choices in OpenRouter response');
		}

		return data.choices[0].message.content;
	}

	private countTokens(systemPrompt: string, userPrompt: string): number {
		try {
			// Use gpt-4 encoding as approximation for Gemini 2.5 Flash
			const enc = encoding_for_model('gpt-4');

			// Count tokens in both prompts
			const combinedText = systemPrompt + userPrompt;
			const tokens = enc.encode(combinedText);
			const tokenCount = tokens.length;

			// Free the encoder
			enc.free();

			return tokenCount;
		} catch (error) {
			console.error('Error counting tokens:', error);
			return 0; // Return 0 if counting fails
		}
	}

	private parseResponse(content: string): Problem {
		const parsed = JSON.parse(content);

		return {
			id: `prob-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
			type: parsed.type,
			question: parsed.question,
			options: parsed.options,
			correctIndex: parsed.correctIndex,
			explanation: parsed.explanation,
			difficultyLevel: parsed.difficulty || 2,
			theme: parsed.theme,
			timestamp: new Date()
		};
	}

	private validateProblem(problem: Problem): boolean {
		// Check required fields
		if (!problem.question || !problem.options || !problem.explanation) {
			console.error('Missing required fields in problem');
			return false;
		}

		// Check exactly 4 options
		if (problem.options.length !== 4) {
			console.error('Problem must have exactly 4 options');
			return false;
		}

		// Check valid correctIndex
		if (problem.correctIndex < 0 || problem.correctIndex > 3) {
			console.error('Invalid correctIndex');
			return false;
		}

		// Check for banned words (content safety)
		const text = `${problem.question} ${problem.options.join(' ')} ${problem.explanation}`;
		const lowerText = text.toLowerCase();

		for (const word of BANNED_WORDS) {
			if (lowerText.includes(word)) {
				console.error('Content safety violation:', word);
				return false;
			}
		}

		return true;
	}

	private async validateProblemLogic(problem: Problem, age: number): Promise<boolean> {
		try {
			// Render validation prompt
			const rendered = this.promptLoader.renderPrompt('validate-problem', {
				question: problem.question,
				options: problem.options,
				correct_answer: problem.options[problem.correctIndex],
				explanation: problem.explanation,
				age
			});

			// Call LLM for validation
			const response = await this.callOpenRouter(rendered);
			const validation = JSON.parse(response);

			if (!validation.valid) {
				console.error('Problem validation failed:', validation.reason, validation.issues);
			}

			return validation.valid === true;
		} catch (error) {
			console.error('Validation step failed, assuming invalid:', error);
			return false;
		}
	}

	private getFallbackProblem(difficultyLevel: number): Problem {
		// Find fallback problem closest to requested difficulty
		const suitable = FALLBACK_PROBLEMS.filter((p) => p.difficultyLevel <= difficultyLevel);

		const fallback =
			suitable.length > 0
				? suitable[Math.floor(Math.random() * suitable.length)]
				: FALLBACK_PROBLEMS[0];

		return {
			...fallback,
			id: `fallback-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
			timestamp: new Date()
		};
	}
}
