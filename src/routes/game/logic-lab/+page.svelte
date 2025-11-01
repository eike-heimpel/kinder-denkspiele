<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	type GamePhase = 'setup' | 'playing' | 'feedback' | 'gameOver';

	// Game state
	let gamePhase = $state<GamePhase>('setup');
	let sessionId = $state<string>('');

	// Setup phase
	let selectedAge = $state<number>(7);
	let guidanceText = $state<string>('');

	// Playing phase
	let currentProblem = $state<{ question: string; options: string[] } | null>(null);
	let score = $state<number>(0);
	let round = $state<number>(0);

	// Feedback phase
	let lastAnswerCorrect = $state<boolean>(false);
	let explanation = $state<string>('');
	let selectedAnswerIndex = $state<number>(-1);

	// Loading states
	let loading = $state<boolean>(false);
	let submitting = $state<boolean>(false);

	// Debug panel (for parents)
	let showDebug = $state<boolean>(false);
	let debugInfo = $state<{
		difficultyLevel?: number;
		consecutiveCorrect?: number;
		consecutiveIncorrect?: number;
		problemType?: string;
		problemDifficulty?: number;
	}>({});

	// URL params
	const userId = $derived($page.url.searchParams.get('userId') || '');

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
					age: selectedAge,
					guidance: guidanceText.trim() || undefined
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
			round = data.round;

			// Update debug info
			debugInfo = {
				difficultyLevel: data.difficultyLevel,
				consecutiveCorrect: data.consecutiveCorrect,
				consecutiveIncorrect: data.consecutiveIncorrect,
				problemType: data.problem?.type,
				problemDifficulty: data.problem?.difficulty
			};

			gamePhase = 'playing';
		} catch (error) {
			console.error('Error starting game:', error);
			alert('Fehler beim Starten des Spiels. Bitte versuche es erneut.');
		} finally {
			loading = false;
		}
	}

	async function resetProgress() {
		if (!confirm('Fortschritt zurücksetzen? Alle bisherigen Fragen werden gelöscht.')) {
			return;
		}

		try {
			await fetch('/api/game/logic-lab/reset', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ userId })
			});

			// Restart game
			gamePhase = 'setup';
			sessionId = '';
			score = 0;
			round = 0;
			currentProblem = null;
		} catch (error) {
			console.error('Error resetting:', error);
			alert('Fehler beim Zurücksetzen.');
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
			round = data.round;

			// Update debug info for next problem
			if (data.nextProblem) {
				debugInfo = {
					difficultyLevel: data.difficultyLevel,
					consecutiveCorrect: data.consecutiveCorrect,
					consecutiveIncorrect: data.consecutiveIncorrect,
					problemType: data.nextProblem.type,
					problemDifficulty: data.nextProblem.difficulty
				};
			}

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

	function continueGame() {
		gamePhase = 'setup';
		sessionId = '';
		currentProblem = null;
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
				<!-- Home Button -->
				<button
					onclick={goHome}
					class="absolute top-4 right-4 px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-700 text-sm"
				>
					🏠 Zurück
				</button>

				<h1 class="text-4xl font-bold text-center mb-2 text-purple-600">🧠 Logik-Labor</h1>
				<p class="text-center text-gray-600 mb-6">
					Unendlich viele Rätsel - dein Fortschritt wird gespeichert!
				</p>

				<!-- Age Selection -->
				<div class="mb-6">
					<label class="block text-lg font-semibold mb-2 text-gray-700"> Wie alt bist du? </label>
					<select
						bind:value={selectedAge}
						class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
					>
						<option value={4}>4 Jahre</option>
						<option value={5}>5 Jahre</option>
						<option value={6}>6 Jahre</option>
						<option value={7}>7 Jahre</option>
						<option value={8}>8 Jahre</option>
						<option value={9}>9 Jahre</option>
						<option value={10}>10 Jahre</option>
					</select>
				</div>

				<!-- Optional Guidance -->
				<div class="mb-6">
					<label class="block text-lg font-semibold mb-2 text-gray-700">
						Themen-Wunsch (optional):
					</label>
					<input
						bind:value={guidanceText}
						placeholder="z.B. 'Fokus auf Weltall' oder 'Mehr Mathe'"
						class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
					/>
					<p class="text-sm text-gray-500 mt-2">
						Optional: Gib einen Themenwunsch an (leer lassen für bunte Mischung)
					</p>
				</div>

				<button
					onclick={startGame}
					disabled={loading}
					class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-2xl font-bold py-4 px-8 rounded-xl hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none mb-4"
				>
					{loading ? 'Lädt...' : 'Weiter spielen! 🚀'}
				</button>

				<button
					onclick={resetProgress}
					class="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm font-semibold py-2 px-4 rounded-xl transition-all"
				>
					🔄 Fortschritt zurücksetzen
				</button>
			</div>
		{:else if gamePhase === 'playing'}
			<!-- Game Screen -->
			<div class="bg-white rounded-3xl shadow-2xl p-8 relative">
				<!-- Debug Toggle (small, top-right) -->
				<button
					onclick={() => (showDebug = !showDebug)}
					class="absolute top-2 right-2 text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-gray-600"
					title="Debug-Info für Eltern"
				>
					{showDebug ? '🔒' : '🔓'} Debug
				</button>

				<!-- Home Button -->
				<button
					onclick={goHome}
					class="absolute top-2 right-12 text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-gray-600"
				>
					🏠
				</button>

				<!-- Header -->
				<div class="flex justify-between items-center mb-6">
					<div class="text-xl font-bold text-purple-600">Frage {round}</div>
					<div class="text-xl font-bold text-green-600">✅ Richtig: {score}</div>
				</div>

				<!-- Debug Panel (expandable) -->
				{#if showDebug}
					<div class="mb-4 p-4 bg-gray-100 rounded-lg border-2 border-gray-300 text-sm">
						<div class="font-bold text-gray-700 mb-2">📊 Debug-Info für Eltern:</div>
						<div class="grid grid-cols-2 gap-2 text-gray-600">
							<div>
								<span class="font-semibold">Schwierigkeitslevel:</span>
								{debugInfo.difficultyLevel ?? '?'}/5
							</div>
							<div>
								<span class="font-semibold">Frage-Schwierigkeit:</span>
								{debugInfo.problemDifficulty ?? '?'}/5
							</div>
							<div>
								<span class="font-semibold">Richtig hintereinander:</span>
								{debugInfo.consecutiveCorrect ?? 0}
							</div>
							<div>
								<span class="font-semibold">Falsch hintereinander:</span>
								{debugInfo.consecutiveIncorrect ?? 0}
							</div>
							<div class="col-span-2">
								<span class="font-semibold">Fragetyp:</span>
								{debugInfo.problemType ?? '?'}
							</div>
						</div>
						<div class="mt-2 text-xs text-gray-500">
							💡 Level steigt nach 2 richtigen Antworten, sinkt nach 2 falschen.
						</div>
					</div>
				{/if}

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

					<div class="text-xl font-bold text-green-600 mb-4">✅ Richtig: {score}</div>

					<p class="text-gray-500">Nächstes Rätsel kommt gleich...</p>
				</div>
			</div>
		{/if}
	</div>
</div>
