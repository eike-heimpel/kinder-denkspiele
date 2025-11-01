<script lang="ts">
	import { speechService } from '$lib/services/speech.service';
	import { onMount } from 'svelte';

	/**
	 * SpeakerButton - Kid-friendly text-to-speech button
	 *
	 * Large, colorful button with speaker icon that reads text aloud.
	 * Designed for easy tapping on tablets by young children.
	 */

	interface Props {
		text: string; // The text to read aloud
		size?: 'sm' | 'md' | 'lg'; // Button size
		variant?: 'primary' | 'secondary'; // Color variant
		disabled?: boolean; // Disable the button
		class?: string; // Additional CSS classes
	}

	let { text, size = 'md', variant = 'primary', disabled = false, class: className = '' }: Props = $props();

	// State
	let isSpeaking = $state(false);
	let isSupported = $state(false);

	// Check browser support on mount
	onMount(() => {
		isSupported = speechService.isSupported();

		// Voices might not be loaded immediately
		if (isSupported && typeof window !== 'undefined') {
			window.speechSynthesis.addEventListener('voiceschanged', () => {
				isSupported = speechService.isSupported();
			});
		}
	});

	// Handle click
	function handleClick() {
		if (disabled || !text) return;

		if (isSpeaking) {
			// Stop current speech
			speechService.stop();
			isSpeaking = false;
		} else {
			// Start speaking
			speechService.speak(text);
			isSpeaking = true;

			// Poll for speech end (Web Speech API doesn't always fire events reliably)
			const checkInterval = setInterval(() => {
				if (!speechService.isSpeaking()) {
					isSpeaking = false;
					clearInterval(checkInterval);
				}
			}, 100);
		}
	}

	// Size classes
	const sizeClasses = {
		sm: 'w-8 h-8 text-base',
		md: 'w-12 h-12 text-xl',
		lg: 'w-16 h-16 text-2xl'
	};

	// Variant classes
	const variantClasses = {
		primary: 'bg-gradient-to-br from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600',
		secondary: 'bg-gradient-to-br from-purple-400 to-pink-400 hover:from-purple-500 hover:to-pink-500'
	};

	// Combine classes
	const buttonClasses = $derived(`
		${sizeClasses[size]}
		${variantClasses[variant]}
		${className}
		rounded-full
		text-white
		font-bold
		flex
		items-center
		justify-center
		shadow-lg
		transition-all
		duration-200
		transform
		${!disabled && !isSpeaking ? 'hover:scale-110 active:scale-95 cursor-pointer' : ''}
		${isSpeaking ? 'animate-pulse scale-110' : ''}
		${disabled ? 'opacity-50 cursor-not-allowed' : ''}
	`.trim().replace(/\s+/g, ' '));
</script>

{#if isSupported}
	<button
		type="button"
		class={buttonClasses}
		onclick={handleClick}
		disabled={disabled}
		aria-label={isSpeaking ? 'Stoppe Vorlesen' : 'Text vorlesen'}
		title={isSpeaking ? 'Stoppe Vorlesen' : 'Text vorlesen'}
	>
		{#if isSpeaking}
			<!-- Pause icon (speaking) -->
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
				class="w-1/2 h-1/2"
			>
				<path d="M5.25 3v18h4.5V3h-4.5zm9 0v18h4.5V3h-4.5z" />
			</svg>
		{:else}
			<!-- Speaker icon (idle) -->
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
				class="w-1/2 h-1/2"
			>
				<path
					d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.318.664-2.66 1.905A9.76 9.76 0 001.5 12c0 .898.121 1.768.35 2.595.341 1.24 1.518 1.905 2.659 1.905h1.93l4.5 4.5c.945.945 2.561.276 2.561-1.06V4.06zM17.78 9.22a.75.75 0 10-1.06 1.06L18.44 12l-1.72 1.72a.75.75 0 001.06 1.06l1.72-1.72 1.72 1.72a.75.75 0 101.06-1.06L20.56 12l1.72-1.72a.75.75 0 00-1.06-1.06l-1.72 1.72-1.72-1.72z"
				/>
			</svg>
		{/if}
	</button>
{/if}
