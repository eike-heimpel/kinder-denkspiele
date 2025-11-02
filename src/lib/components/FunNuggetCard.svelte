<script lang="ts">
	import Card from './Card.svelte';

	let { text }: { text: string } = $props();
</script>

{#if text}
	<Card>
		<div class="flex items-start gap-3">
			<span class="text-3xl flex-shrink-0">💡</span>
			<p class="text-base text-purple-700 font-medium leading-relaxed pt-1">{text}</p>
		</div>
	</Card>
{/if}
