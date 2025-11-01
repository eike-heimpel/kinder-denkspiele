/**
 * Speech Service - Web Speech API wrapper for German text-to-speech
 *
 * Provides a simple interface for reading German text aloud using the browser's
 * built-in speech synthesis. Designed for kid-friendly applications.
 */

export class SpeechService {
	private synth: SpeechSynthesis | null = null;
	private currentUtterance: SpeechSynthesisUtterance | null = null;

	constructor() {
		if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
			this.synth = window.speechSynthesis;
		}
	}

	/**
	 * Check if speech synthesis is supported in the current browser
	 */
	isSupported(): boolean {
		return this.synth !== null;
	}

	/**
	 * Get available German voices
	 */
	getGermanVoices(): SpeechSynthesisVoice[] {
		if (!this.synth) return [];

		const voices = this.synth.getVoices();
		return voices.filter(voice => voice.lang.startsWith('de'));
	}

	/**
	 * Select the best German voice available
	 * Prioritizes female voices and German locale
	 */
	private selectGermanVoice(): SpeechSynthesisVoice | null {
		const germanVoices = this.getGermanVoices();

		if (germanVoices.length === 0) return null;

		// Prefer de-DE voices
		const deDE = germanVoices.find(v => v.lang === 'de-DE');
		if (deDE) return deDE;

		// Fall back to any German voice
		return germanVoices[0];
	}

	/**
	 * Speak the given German text
	 * @param text - The German text to read aloud
	 * @param options - Optional speech configuration
	 */
	speak(text: string, options: { rate?: number; pitch?: number; volume?: number } = {}): void {
		if (!this.synth) {
			console.warn('Speech synthesis not supported in this browser');
			return;
		}

		// Stop any current speech
		this.stop();

		// Create new utterance
		const utterance = new SpeechSynthesisUtterance(text);

		// Set German language
		utterance.lang = 'de-DE';

		// Try to use a German voice
		const germanVoice = this.selectGermanVoice();
		if (germanVoice) {
			utterance.voice = germanVoice;
		}

		// Apply options with kid-friendly defaults
		utterance.rate = options.rate ?? 0.9; // Slightly slower for comprehension
		utterance.pitch = options.pitch ?? 1.1; // Slightly higher for kid-friendliness
		utterance.volume = options.volume ?? 1.0;

		// Store current utterance
		this.currentUtterance = utterance;

		// Speak
		this.synth.speak(utterance);
	}

	/**
	 * Stop any currently playing speech
	 */
	stop(): void {
		if (this.synth) {
			this.synth.cancel();
			this.currentUtterance = null;
		}
	}

	/**
	 * Check if speech is currently playing
	 */
	isSpeaking(): boolean {
		return this.synth?.speaking ?? false;
	}

	/**
	 * Pause the current speech
	 */
	pause(): void {
		if (this.synth && this.synth.speaking) {
			this.synth.pause();
		}
	}

	/**
	 * Resume paused speech
	 */
	resume(): void {
		if (this.synth && this.synth.paused) {
			this.synth.resume();
		}
	}
}

// Export singleton instance
export const speechService = new SpeechService();
