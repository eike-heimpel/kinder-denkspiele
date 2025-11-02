<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';

	interface StorySession {
		session_id: string;
		character_name: string;
		story_theme: string;
		round: number;
		lastUpdated: string;
		first_image_url: string;
		createdAt: string;
	}

	let userId = $state('');
	let sessions = $state<StorySession[]>([]);
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		userId = $page.url.searchParams.get('userId') || '';

		if (!userId) {
			goto('/');
			return;
		}

		try {
			const response = await fetch(`/api/game/maerchenweber/sessions?userId=${userId}`);

			if (!response.ok) {
				throw new Error('Failed to fetch sessions');
			}

			const data = await response.json();
			sessions = data.sessions || [];
		} catch (err) {
			error = 'Fehler beim Laden der Geschichten. Ist der Backend-Server gestartet?';
			console.error('Error loading sessions:', err);
		} finally {
			loading = false;
		}
	});

	function continueStory(sessionId: string) {
		goto(`/game/maerchenweber?userId=${userId}&sessionId=${sessionId}`);
	}

	function viewStory(sessionId: string) {
		goto(`/game/maerchenweber/replay/${sessionId}`);
	}

	function newStory() {
		goto(`/game/maerchenweber?userId=${userId}`);
	}

	function formatDate(isoDate: string): string {
		if (!isoDate) return '';
		const date = new Date(isoDate);
		return date.toLocaleDateString('de-DE', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-8">
	<div class="max-w-7xl mx-auto">
		<!-- Header -->
		<div class="mb-8 flex justify-between items-center">
			<div>
				<h1 class="text-5xl font-bold text-white mb-2">📖 Meine Geschichten</h1>
				<p class="text-xl text-white/90">Alle deine Märchen-Abenteuer</p>
			</div>
			<div class="flex gap-4">
				<Button
					variant="secondary"
					onclick={() => goto('/')}
					class="bg-white/20 hover:bg-white/30 text-white"
				>
					← Zurück
				</Button>
				<Button variant="primary" onclick={newStory} class="bg-white text-purple-600 hover:bg-white/90">
					✨ Neue Geschichte
				</Button>
			</div>
		</div>

		<!-- Loading State -->
		{#if loading}
			<div class="text-center py-20">
				<div class="text-6xl mb-4">⏳</div>
				<p class="text-2xl text-white">Lade Geschichten...</p>
			</div>
		{:else if error}
			<!-- Error State -->
			<Card class="text-center py-12">
				<div class="text-6xl mb-4">❌</div>
				<h2 class="text-2xl font-bold mb-4">Fehler</h2>
				<p class="text-gray-600 mb-6">{error}</p>
				<Button variant="primary" onclick={() => goto('/')}>Zurück zur Startseite</Button>
			</Card>
		{:else if sessions.length === 0}
			<!-- Empty State -->
			<Card class="text-center py-20">
				<div class="text-8xl mb-6">📚</div>
				<h2 class="text-3xl font-bold mb-4">Noch keine Geschichten</h2>
				<p class="text-xl text-gray-600 mb-8">
					Beginne dein erstes magisches Abenteuer!
				</p>
				<Button variant="primary" onclick={newStory} class="text-xl px-8 py-4">
					✨ Erste Geschichte erstellen
				</Button>
			</Card>
		{:else}
			<!-- Stories Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each sessions as session}
					<Card class="overflow-hidden hover:shadow-2xl transition-shadow duration-300">
						<!-- Story Thumbnail -->
						{#if session.first_image_url}
							<div class="w-full h-48 overflow-hidden bg-gray-200">
								<img
									src={session.first_image_url}
									alt={session.character_name}
									class="w-full h-full object-cover"
								/>
							</div>
						{:else}
							<div
								class="w-full h-48 bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center"
							>
								<div class="text-8xl">📖</div>
							</div>
						{/if}

						<!-- Story Info -->
						<div class="p-6">
							<h3 class="text-2xl font-bold mb-2 text-gray-800">
								{session.character_name}
							</h3>
							<p class="text-gray-600 mb-4 line-clamp-2">
								{session.story_theme}
							</p>

							<div class="flex items-center gap-4 text-sm text-gray-500 mb-4">
								<span class="flex items-center gap-1">
									🎯 Runde {session.round}
								</span>
								<span class="flex items-center gap-1">
									🕐 {formatDate(session.lastUpdated)}
								</span>
							</div>

							<!-- Action Buttons -->
							<div class="flex gap-2">
								<Button
									variant="primary"
									onclick={() => continueStory(session.session_id)}
									class="flex-1 text-sm"
								>
									▶️ Weiterspielen
								</Button>
								<Button
									variant="secondary"
									onclick={() => viewStory(session.session_id)}
									class="text-sm"
								>
									👁️ Ansehen
								</Button>
							</div>
						</div>
					</Card>
				{/each}
			</div>

			<!-- Summary Stats -->
			<div class="mt-8 text-center text-white/80">
				<p class="text-lg">
					📚 Du hast <strong class="text-white">{sessions.length}</strong>
					{sessions.length === 1 ? 'Geschichte' : 'Geschichten'} erstellt
				</p>
			</div>
		{/if}
	</div>
</div>
