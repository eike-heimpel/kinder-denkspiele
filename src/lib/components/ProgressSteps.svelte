<script lang="ts">
	import { onMount } from 'svelte';
	import Card from './Card.svelte';

	let {
		isStarting = false
	}: {
		isStarting?: boolean;
	} = $props();

	// Steps with estimated timing
	const steps = [
		{ name: 'Geschichte schreiben', duration: 7000, emoji: '📝' },
		{ name: 'Entscheidungen erstellen', duration: 5000, emoji: '🎨' },
		{ name: 'Bild malen', duration: 10000, emoji: '🖼️' }
	];

	let currentStepIndex = $state(0);
	let elapsedTime = $state(0);

	onMount(() => {
		const startTime = Date.now();

		const interval = setInterval(() => {
			elapsedTime = Date.now() - startTime;

			// Calculate which step we should be on based on elapsed time
			let cumulativeTime = 0;
			for (let i = 0; i < steps.length; i++) {
				cumulativeTime += steps[i].duration;
				if (elapsedTime < cumulativeTime) {
					currentStepIndex = i;
					break;
				} else if (i === steps.length - 1) {
					currentStepIndex = i; // Stay on last step
				}
			}
		}, 100);

		return () => clearInterval(interval);
	});
</script>

<Card>
	<div class="space-y-3">
		{#each steps as step, index}
			<div class="flex items-center gap-3">
				{#if index < currentStepIndex}
					<!-- Completed step -->
					<span class="text-2xl">✓</span>
					<span class="text-sm text-gray-500 line-through">{step.name}</span>
				{:else if index === currentStepIndex}
					<!-- Current step -->
					<span class="text-2xl animate-pulse">{step.emoji}</span>
					<span class="text-base font-semibold text-purple-700">{step.name}...</span>
				{:else}
					<!-- Future step -->
					<span class="text-2xl opacity-30">{step.emoji}</span>
					<span class="text-sm text-gray-400">{step.name}</span>
				{/if}
			</div>
		{/each}
	</div>
</Card>
