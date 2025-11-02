<script lang="ts">
	import Card from './Card.svelte';

	let { choices = [] }: { choices: string[] } = $props();
</script>

{#if choices.length > 0}
	<Card>
		<div class="space-y-3">
			<div class="flex items-center gap-2 mb-4">
				<span class="text-2xl">🧵</span>
				<h3 class="text-lg font-semibold text-purple-700">Deine Reise bisher:</h3>
			</div>

			<div class="space-y-2 max-h-48 overflow-y-auto">
				{#each choices as choice, index}
					<div class="flex items-start gap-2 pl-2">
						<span class="text-amber-500 flex-shrink-0 mt-0.5">✨</span>
						<p class="text-sm text-gray-700 leading-relaxed">{choice}</p>
					</div>
				{/each}
			</div>
		</div>
	</Card>
{/if}
