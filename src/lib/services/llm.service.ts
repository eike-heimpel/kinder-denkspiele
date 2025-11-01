import { OPENROUTER_API_KEY } from '$env/static/private';
import { PromptLoader, type RenderedPrompt } from './prompt-loader.service';

export interface GenerateProblemParams {
	initialGuidance?: string;
	age: number;
	difficulty: 'easy' | 'hard';
	problemType: 'riddle' | 'pattern' | 'category' | 'cause-effect';
	performanceHistory: Array<{
		question: string;
		type: string;
		difficulty: number;
		correct: boolean;
	}>;
	consecutiveCorrect: number;
	consecutiveIncorrect: number;
}

export interface Problem {
	id: string;
	type: 'riddle' | 'pattern' | 'category' | 'cause-effect';
	question: string;
	options: string[];
	correctIndex: number;
	explanation: string;
	difficultyLevel: number;
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
		type: 'riddle',
		question: 'Welches Tier macht "Wuff"?',
		options: ['Katze', 'Hund', 'Vogel', 'Maus'],
		correctIndex: 1,
		explanation: 'Der Hund macht "Wuff"!',
		difficultyLevel: 1
	},
	{
		type: 'category',
		question: 'Welches ist KEIN Tier?',
		options: ['Hund', 'Katze', 'Baum', 'Vogel'],
		correctIndex: 2,
		explanation: 'Der Baum ist eine Pflanze, kein Tier.',
		difficultyLevel: 1
	},
	{
		type: 'pattern',
		question: 'Was kommt als nächstes? 1, 2, 3, ___',
		options: ['4', '5', '2', '1'],
		correctIndex: 0,
		explanation: 'Die Zahlen zählen hoch: 1, 2, 3, 4!',
		difficultyLevel: 2
	},
	{
		type: 'cause-effect',
		question: 'Was passiert, wenn es regnet?',
		options: ['Es wird nass', 'Es wird heiß', 'Es wird dunkel', 'Es schneit'],
		correctIndex: 0,
		explanation: 'Wenn es regnet, wird alles nass!',
		difficultyLevel: 2
	},
	{
		type: 'riddle',
		question: 'Ich bin gelb und leuchte am Himmel am Tag. Was bin ich?',
		options: ['Mond', 'Sonne', 'Stern', 'Lampe'],
		correctIndex: 1,
		explanation: 'Die Sonne ist gelb und leuchtet am Tag!',
		difficultyLevel: 2
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
				problem_type: params.problemType,
				performance_history: params.performanceHistory,
				consecutive_correct: params.consecutiveCorrect,
				consecutive_incorrect: params.consecutiveIncorrect
			});

			// Call OpenRouter API
			const response = await this.callOpenRouter(rendered);

			// Parse and validate response
			const problem = this.parseResponse(response);

			if (!this.validateProblem(problem)) {
				console.error('Generated problem failed validation');
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
