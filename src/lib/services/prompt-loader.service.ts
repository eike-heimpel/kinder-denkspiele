import fs from 'fs';
import path from 'path';
import yaml from 'yaml';
import nunjucks from 'nunjucks';

interface PromptConfig {
	version: string;
	model: string;
	temperature: number;
	max_tokens: number;
	response_format?: { type: string };
	system_prompt: string;
	user_prompt: string;
	variables: Array<{
		name: string;
		type: string;
		required: boolean;
		description: string;
	}>;
}

export interface RenderedPrompt {
	model: string;
	temperature: number;
	max_tokens: number;
	response_format?: { type: string };
	system_prompt: string;
	user_prompt: string;
}

export class PromptLoader {
	private promptsDir: string;
	private env: nunjucks.Environment;

	constructor() {
		this.promptsDir = path.join(process.cwd(), 'src', 'lib', 'prompts');
		this.env = nunjucks.configure({ autoescape: false });
	}

	loadPrompt(promptName: string): PromptConfig {
		const promptPath = path.join(this.promptsDir, `${promptName}.yaml`);
		const content = fs.readFileSync(promptPath, 'utf-8');
		return yaml.parse(content);
	}

	renderPrompt(promptName: string, variables: Record<string, any>): RenderedPrompt {
		const config = this.loadPrompt(promptName);

		// Validate required variables
		for (const varDef of config.variables) {
			if (varDef.required && !(varDef.name in variables)) {
				throw new Error(`Missing required variable: ${varDef.name}`);
			}
		}

		// Render prompts with Jinja2 syntax via Nunjucks
		const systemPrompt = this.env.renderString(config.system_prompt, variables);
		const userPrompt = this.env.renderString(config.user_prompt, variables);

		return {
			model: config.model,
			temperature: config.temperature,
			max_tokens: config.max_tokens,
			response_format: config.response_format,
			system_prompt: systemPrompt,
			user_prompt: userPrompt
		};
	}
}
