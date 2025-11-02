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

	function startNewStory() {
		goto(`/game/maerchenweber/play?userId=${userId}`);
	}

	function continueStory(sessionId: string) {
		goto(`/game/maerchenweber/play?userId=${userId}&sessionId=${sessionId}`);
	}

	function viewStory(sessionId: string) {
		goto(`/game/maerchenweber/replay/${sessionId}`);
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

<svelte:head>
	<title>Märchenweber - Kinder Denkspiele</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-8">
	<div class="max-w-7xl mx-auto">
		<!-- Header Section -->
		<div class="text-center mb-12">
			<div class="flex justify-between items-center mb-8">
				<Button variant="secondary" onclick={() => goto('/')} class="text-lg">
					← Zurück
				</Button>
				<div></div>
			</div>

			<h1 class="text-6xl font-black text-amber-900 mb-4 flex items-center justify-center gap-4">
				📖 Märchenweber
			</h1>
			<p class="text-2xl text-amber-700 mb-8">
				Erlebe magische Abenteuer und schreibe deine eigenen Geschichten!
			</p>

			<!-- Big Start New Story Button -->
			<Button
				variant="primary"
				onclick={startNewStory}
				class="text-2xl px-12 py-6 bg-amber-500 hover:bg-amber-600 text-white shadow-2xl transform hover:scale-105 transition-transform"
			>
				✨ Neue Geschichte beginnen
			</Button>
		</div>

		<!-- Divider -->
		{#if !loading && sessions.length > 0}
			<div class="my-12 flex items-center gap-4">
				<div class="flex-1 h-px bg-amber-300"></div>
				<h2 class="text-3xl font-bold text-amber-800">Deine Geschichten</h2>
				<div class="flex-1 h-px bg-amber-300"></div>
			</div>
		{/if}

		<!-- Loading State -->
		{#if loading}
			<div class="text-center py-20">
				<div
					class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-amber-500 border-t-transparent mb-4"
				></div>
				<p class="text-2xl text-amber-800">Lade Geschichten...</p>
			</div>
		{:else if error}
			<!-- Error State -->
			<Card class="text-center py-12 bg-red-50 border-2 border-red-300">
				<div class="text-6xl mb-4">❌</div>
				<h2 class="text-2xl font-bold mb-4 text-red-800">Fehler</h2>
				<p class="text-red-600 mb-6">{error}</p>
				<p class="text-sm text-gray-600">
					Tipp: Stelle sicher, dass der FastAPI Backend-Server läuft (Port 8000)
				</p>
			</Card>
		{:else if sessions.length === 0}
			<!-- Empty State -->
			<Card class="text-center py-20 bg-gradient-to-br from-amber-100 to-yellow-100">
				<div class="text-9xl mb-6">📚</div>
				<h2 class="text-4xl font-bold mb-4 text-amber-900">Noch keine Geschichten</h2>
				<p class="text-xl text-amber-700 mb-8">
					Klicke oben auf "Neue Geschichte beginnen", um dein erstes magisches Abenteuer zu
					starten!
				</p>
			</Card>
		{:else}
			<!-- Stories Gallery -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each sessions as session}
					<Card
						class="overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2"
					>
						<!-- Story Thumbnail -->
						{#if session.first_image_url}
							<div class="w-full h-56 overflow-hidden bg-gray-200">
								<img
									src={session.first_image_url}
									alt={session.character_name}
									class="w-full h-full object-cover"
								/>
							</div>
						{:else}
							<div
								class="w-full h-56 bg-gradient-to-br from-purple-400 via-pink-400 to-amber-400 flex items-center justify-center"
							>
								<div class="text-9xl">📖</div>
							</div>
						{/if}

						<!-- Story Info -->
						<div class="p-6">
							<h3 class="text-2xl font-bold mb-2 text-gray-800 truncate">
								{session.character_name}
							</h3>
							<p class="text-gray-600 mb-4 line-clamp-2">
								{session.story_theme}
							</p>

							<div class="flex items-center gap-4 text-sm text-gray-500 mb-4">
								<span class="flex items-center gap-1">
									🎯 <strong>Runde {session.round}</strong>
								</span>
								<span class="flex items-center gap-1 text-xs">
									🕐 {formatDate(session.lastUpdated).split(',')[0]}
								</span>
							</div>

							<!-- Action Buttons -->
							<div class="flex gap-2">
								<Button
									variant="primary"
									onclick={() => continueStory(session.session_id)}
									class="flex-1 text-sm bg-amber-500 hover:bg-amber-600"
								>
									▶️ Weiterspielen
								</Button>
								<Button
									variant="secondary"
									onclick={() => viewStory(session.session_id)}
									class="text-sm"
								>
									👁️
								</Button>
							</div>
						</div>
					</Card>
				{/each}
			</div>

			<!-- Summary Stats -->
			<div class="mt-12 text-center">
				<Card class="inline-block bg-amber-100 border-2 border-amber-300">
					<p class="text-lg text-amber-800">
						📚 Du hast <strong class="text-2xl text-amber-900">{sessions.length}</strong>
						{sessions.length === 1 ? 'Geschichte' : 'Geschichten'} erstellt
					</p>
				</Card>
			</div>
		{/if}
	</div>
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
