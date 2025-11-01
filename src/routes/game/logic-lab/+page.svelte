<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	type GamePhase = 'setup' | 'playing' | 'feedback' | 'gameOver';

	// Game state
	let gamePhase = $state<GamePhase>('setup');
	let sessionId = $state<string>('');

	// Setup phase
	let initialGuidance = $state<string>('');

	// Playing phase
	let currentProblem = $state<{ question: string; options: string[] } | null>(null);
	let score = $state<number>(0);
	let lives = $state<number>(3);
	let round = $state<number>(0);
	let totalRounds = $state<number>(5);

	// Feedback phase
	let lastAnswerCorrect = $state<boolean>(false);
	let explanation = $state<string>('');
	let selectedAnswerIndex = $state<number>(-1);

	// Loading states
	let loading = $state<boolean>(false);
	let submitting = $state<boolean>(false);

	// URL params
	const userId = $derived($page.url.searchParams.get('userId') || '');
	const difficulty = $derived(
		($page.url.searchParams.get('difficulty') as 'easy' | 'hard') || 'easy'
	);

	onMount(() => {
		if (!userId) {
			goto('/');
		}
	});

	async function startGame() {
		loading = true;

		try {
			const response = await fetch('/api/game/logic-lab/start', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					userId,
					difficulty,
					initialGuidance: initialGuidance.trim() || undefined
				})
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.error || 'Failed to start game');
			}

			const data = await response.json();
			sessionId = data.sessionId;
			currentProblem = data.problem;
			score = data.score;
			lives = data.lives;
			round = data.round;
			totalRounds = data.totalRounds;
			gamePhase = 'playing';
		} catch (error) {
			console.error('Error starting game:', error);
			alert('Fehler beim Starten des Spiels. Bitte versuche es erneut.');
		} finally {
			loading = false;
		}
	}

	async function submitAnswer(answerIndex: number) {
		if (submitting) return;

		submitting = true;
		selectedAnswerIndex = answerIndex;

		try {
			const response = await fetch('/api/game/logic-lab/answer', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ sessionId, answerIndex })
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.error || 'Failed to submit answer');
			}

			const data = await response.json();
			lastAnswerCorrect = data.correct;
			explanation = data.explanation;
			score = data.score;
			lives = data.lives;
			round = data.round;

			// Show feedback
			gamePhase = 'feedback';

			// Auto-advance after 3 seconds
			setTimeout(() => {
				if (data.gameOver) {
					gamePhase = 'gameOver';
				} else {
					currentProblem = data.nextProblem;
					selectedAnswerIndex = -1;
					gamePhase = 'playing';
				}
				submitting = false;
			}, 3000);
		} catch (error) {
			console.error('Error submitting answer:', error);
			alert('Fehler beim Senden der Antwort. Bitte versuche es erneut.');
			submitting = false;
		}
	}

	function playAgain() {
		gamePhase = 'setup';
		sessionId = '';
		initialGuidance = '';
		currentProblem = null;
		score = 0;
		lives = 3;
		round = 0;
		selectedAnswerIndex = -1;
	}

	function goHome() {
		goto('/');
	}
</script>

<div
	class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 flex items-center justify-center p-4"
>
	<div class="max-w-2xl w-full">
		{#if gamePhase === 'setup'}
			<!-- Setup Screen -->
			<div class="bg-white rounded-3xl shadow-2xl p-8">
				<h1 class="text-4xl font-bold text-center mb-2 text-purple-600">🧠 Logik-Labor</h1>
				<p class="text-center text-gray-600 mb-6">
					Löse spannende Rätsel und zeige dein Können!
				</p>

				<div class="mb-6">
					<label class="block text-lg font-semibold mb-2 text-gray-700">
						Hilf uns, die besten Rätsel für dich zu finden:
					</label>
					<textarea
						bind:value={initialGuidance}
						placeholder="z.B. 'Mein Kind ist 7 Jahre alt und liebt Tiere' oder 'Mathe ist noch schwierig'"
						class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none text-lg resize-none"
						rows="3"
					></textarea>
					<p class="text-sm text-gray-500 mt-2">
						Optional: Diese Info hilft uns, passende Rätsel zu erstellen.
					</p>
				</div>

				<button
					onclick={startGame}
					disabled={loading}
					class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-2xl font-bold py-4 px-8 rounded-xl hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
				>
					{loading ? 'Lädt...' : 'Spiel starten! 🚀'}
				</button>
			</div>
		{:else if gamePhase === 'playing'}
			<!-- Game Screen -->
			<div class="bg-white rounded-3xl shadow-2xl p-8">
				<!-- Header -->
				<div class="flex justify-between items-center mb-6">
					<div class="text-xl font-bold text-purple-600">
						Runde {round}/{totalRounds}
					</div>
					<div class="flex gap-4 items-center">
						<div class="text-xl font-bold text-green-600">Punkte: {score}</div>
						<div class="text-xl font-bold text-red-600">
							{'❤️'.repeat(lives)}
							{'🖤'.repeat(3 - lives)}
						</div>
					</div>
				</div>

				<!-- Problem Question -->
				{#if currentProblem}
					<div class="mb-8">
						<div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl p-6">
							<p class="text-2xl font-bold text-center text-gray-800">
								{currentProblem.question}
							</p>
						</div>
					</div>

					<!-- Answer Options -->
					<div class="grid grid-cols-1 gap-4">
						{#each currentProblem.options as option, index}
							<button
								onclick={() => submitAnswer(index)}
								disabled={submitting}
								class="bg-gradient-to-r from-blue-400 to-blue-500 text-white text-xl font-bold py-6 px-8 rounded-xl hover:from-blue-500 hover:to-blue-600 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-left"
							>
								<span class="inline-block w-8">{String.fromCharCode(65 + index)}.</span>
								{option}
							</button>
						{/each}
					</div>
				{/if}
			</div>
		{:else if gamePhase === 'feedback'}
			<!-- Feedback Screen -->
			<div class="bg-white rounded-3xl shadow-2xl p-8">
				<div class="text-center">
					{#if lastAnswerCorrect}
						<div class="text-8xl mb-4">✅</div>
						<h2 class="text-4xl font-bold text-green-600 mb-4">Richtig!</h2>
					{:else}
						<div class="text-8xl mb-4">❌</div>
						<h2 class="text-4xl font-bold text-red-600 mb-4">Nicht ganz...</h2>
					{/if}

					<div class="bg-gray-100 rounded-2xl p-6 mb-6">
						<p class="text-xl text-gray-800">{explanation}</p>
					</div>

					<div class="flex justify-center items-center gap-4">
						<div class="text-xl font-bold text-green-600">Punkte: {score}</div>
						<div class="text-xl font-bold text-red-600">
							{'❤️'.repeat(lives)}
							{'🖤'.repeat(3 - lives)}
						</div>
					</div>

					<p class="text-gray-500 mt-4">Nächstes Rätsel kommt gleich...</p>
				</div>
			</div>
		{:else if gamePhase === 'gameOver'}
			<!-- Game Over Screen -->
			<div class="bg-white rounded-3xl shadow-2xl p-8">
				<div class="text-center">
					<div class="text-8xl mb-4">🎉</div>
					<h2 class="text-4xl font-bold text-purple-600 mb-4">Spiel beendet!</h2>

					<div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl p-6 mb-6">
						<p class="text-3xl font-bold text-gray-800 mb-2">Deine Punktzahl:</p>
						<p class="text-6xl font-bold text-purple-600">{score} / {totalRounds}</p>
					</div>

					<div class="grid grid-cols-2 gap-4">
						<button
							onclick={playAgain}
							class="bg-gradient-to-r from-green-500 to-green-600 text-white text-xl font-bold py-4 px-6 rounded-xl hover:from-green-600 hover:to-green-700 transform hover:scale-105 transition-all"
						>
							🔄 Nochmal spielen
						</button>
						<button
							onclick={goHome}
							class="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xl font-bold py-4 px-6 rounded-xl hover:from-blue-600 hover:to-blue-700 transform hover:scale-105 transition-all"
						>
							🏠 Zurück
						</button>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
