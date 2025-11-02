<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';

	interface ImageHistoryEntry {
		round: number;
		url: string;
		description: string;
	}

	let sessionId = $state('');
	let userId = $state('');
	let characterName = $state('');
	let characterDescription = $state('');
	let storyTheme = $state('');
	let history = $state<string[]>([]);
	let imageHistory = $state<ImageHistoryEntry[]>([]);
	let round = $state(1);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		sessionId = $page.params.sessionId;

		if (!sessionId) {
			goto('/');
			return;
		}

		try {
			const response = await fetch(`/api/game/maerchenweber/session/${sessionId}`);

			if (!response.ok) {
				throw new Error('Session not found');
			}

			const session = await response.json();

			// Extract data
			userId = session.userId;
			characterName = session.character_name || 'Unbekannt';
			characterDescription = session.character_description || '';
			storyTheme = session.story_theme || '';
			history = session.history || [];
			imageHistory = session.image_history || [];
			round = session.round || 1;

			console.log(`Loaded session for replay: ${sessionId}`);
		} catch (err) {
			error = 'Fehler beim Laden der Geschichte. Bitte versuche es erneut.';
			console.error('Error loading session:', err);
		} finally {
			loading = false;
		}
	});

	function getImageForIndex(index: number): string | null {
		// Images are generated every 5 turns
		// Round 1 has image at index 0 (after first story)
		// Round 6 has image at index 1, etc.

		// Calculate which round this index represents
		// Each turn adds: story + choice, so index 0 = round 1 story, index 1 = round 1 choice
		const storyRound = Math.floor(index / 2) + 1;

		// Find image for this round
		const image = imageHistory.find((img) => img.round === storyRound);
		return image ? image.url : null;
	}

	function isChoice(text: string): boolean {
		return text.startsWith('[Wahl]:');
	}

	function formatChoice(text: string): string {
		return text.replace('[Wahl]: ', '');
	}

	function continueStory() {
		if (userId) {
			goto(`/game/maerchenweber?userId=${userId}&sessionId=${sessionId}`);
		}
	}

	function backToStories() {
		if (userId) {
			goto(`/game/maerchenweber/stories?userId=${userId}`);
		} else {
			goto('/');
		}
	}
</script>

<svelte:head>
	<title>Geschichte ansehen - Märchenweber</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-100 to-orange-100 p-8">
	<div class="max-w-4xl mx-auto">
		<!-- Header -->
		<div class="mb-8 flex justify-between items-center">
			<div>
				<h1 class="text-4xl font-bold text-amber-900 mb-2">📖 {characterName}</h1>
				<p class="text-xl text-amber-700">{storyTheme}</p>
			</div>
			<div class="flex gap-4">
				<Button variant="secondary" onclick={backToStories}>← Zurück zu Geschichten</Button>
				<Button variant="primary" onclick={continueStory}>▶️ Weiterspielen</Button>
			</div>
		</div>

		<!-- Loading State -->
		{#if loading}
			<Card>
				<div class="text-center py-12">
					<div
						class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-amber-500 border-t-transparent mb-4"
					></div>
					<p class="text-xl font-semibold text-gray-700">Geschichte wird geladen...</p>
				</div>
			</Card>
		{:else if error}
			<!-- Error State -->
			<Card>
				<div class="text-center py-12">
					<div class="text-6xl mb-4">❌</div>
					<h2 class="text-2xl font-bold mb-4">Fehler</h2>
					<p class="text-gray-600 mb-6">{error}</p>
					<Button variant="primary" onclick={() => goto('/')}>Zurück zur Startseite</Button>
				</div>
			</Card>
		{:else}
			<!-- Story Content -->
			<div class="space-y-6">
				<!-- Story Info Card -->
				<Card>
					<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
						<div>
							<div class="text-3xl mb-1">🎭</div>
							<div class="text-sm text-gray-600">Charakter</div>
							<div class="font-semibold">{characterName}</div>
						</div>
						<div>
							<div class="text-3xl mb-1">📍</div>
							<div class="text-sm text-gray-600">Ort</div>
							<div class="font-semibold line-clamp-1">{storyTheme}</div>
						</div>
						<div>
							<div class="text-3xl mb-1">🎯</div>
							<div class="text-sm text-gray-600">Runde</div>
							<div class="font-semibold">{round}</div>
						</div>
						<div>
							<div class="text-3xl mb-1">📝</div>
							<div class="text-sm text-gray-600">Abschnitte</div>
							<div class="font-semibold">{history.length}</div>
						</div>
					</div>
				</Card>

				<!-- Story Timeline -->
				<div class="space-y-6">
					{#each history as item, index}
						{@const itemIsChoice = isChoice(item)}
						{@const imageUrl = getImageForIndex(index)}

						{#if itemIsChoice}
							<!-- User Choice -->
							<div class="flex items-center gap-4">
								<div class="flex-shrink-0 w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
									<span class="text-2xl">👆</span>
								</div>
								<Card class="flex-1 bg-blue-50 border-2 border-blue-300">
									<p class="text-lg font-medium text-blue-900">
										{formatChoice(item)}
									</p>
								</Card>
							</div>
						{:else}
							<!-- Story Segment -->
							<div class="space-y-4">
								<!-- Story Text -->
								<div class="flex items-start gap-4">
									<div class="flex-shrink-0 w-12 h-12 bg-amber-500 rounded-full flex items-center justify-center">
										<span class="text-2xl">📖</span>
									</div>
									<Card class="flex-1">
										<p class="text-lg leading-relaxed text-gray-800 whitespace-pre-wrap">
											{item}
										</p>
									</Card>
								</div>

								<!-- Image (if available) -->
								{#if imageUrl}
									<div class="ml-16">
										<Card class="overflow-hidden">
											<img
												src={imageUrl}
												alt="Geschichtsbild"
												class="w-full h-64 md:h-96 object-cover rounded-lg"
												loading="lazy"
											/>
										</Card>
									</div>
								{/if}
							</div>
						{/if}
					{/each}
				</div>

				<!-- Footer Actions -->
				<div class="flex justify-center gap-4 pt-8">
					<Button variant="secondary" onclick={backToStories}>← Alle Geschichten</Button>
					<Button variant="primary" onclick={continueStory} class="text-lg px-8 py-4">
						▶️ Geschichte fortsetzen
					</Button>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.line-clamp-1 {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
