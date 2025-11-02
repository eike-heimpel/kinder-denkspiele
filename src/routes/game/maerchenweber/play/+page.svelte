<script lang="ts">
	import { onMount } from "svelte";
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";
	import Button from "$lib/components/Button.svelte";
	import Card from "$lib/components/Card.svelte";
	import JourneyRecap from "$lib/components/JourneyRecap.svelte";
	import FunNuggetCard from "$lib/components/FunNuggetCard.svelte";
	import ProgressSteps from "$lib/components/ProgressSteps.svelte";

	type GamePhase = "setup" | "playing" | "loading" | "gameOver";

	// Game state
	let gamePhase = $state<GamePhase>("setup");
	let sessionId = $state<string>("");

	// Setup phase
	let characterName = $state<string>("");
	let characterDescription = $state<string>("");
	let storyTheme = $state<string>("");

	// Playing phase
	let currentStory = $state<string>("");
	let currentImageUrl = $state<string | null>(null);
	let currentChoices = $state<string[]>([]);
	let round = $state<number>(1);

	// Waiting UX engagement
	let funNugget = $state<string>("");
	let choicesHistory = $state<string[]>([]);

	// Image polling state
	let imageLoading = $state<boolean>(false);
	let imageError = $state<boolean>(false);
	let imageErrorMessage = $state<string>("");
	let imageRetryAfter = $state<number>(5);
	let pollInterval: number | null = null;
	let pollTimeout: number | null = null;

	// General error state
	let errorMessage = $state<string>("");
	let showError = $state<boolean>(false);

	// Loading state
	let loading = $state<boolean>(false);
	let isStarting = $state<boolean>(false);

	// Debug state
	let debugMode = $state<boolean>(false);
	let lastTiming = $state<any>(null);
	let lastError = $state<any>(null);
	let warnings = $state<string[]>([]);

	// URL params
	const userId = $derived($page.url.searchParams.get("userId") || "");
	const existingSessionId = $derived(
		$page.url.searchParams.get("sessionId") || "",
	);

	onMount(async () => {
		if (!userId) {
			goto("/");
			return;
		}

		// Check if we're continuing an existing session
		if (existingSessionId) {
			await loadExistingSession(existingSessionId);
		}

		// Cleanup polling on unmount
		return () => {
			if (pollInterval) clearInterval(pollInterval);
			if (pollTimeout) clearTimeout(pollTimeout);
		};
	});

	async function loadExistingSession(sessionIdToLoad: string) {
		try {
			loading = true;
			gamePhase = "loading";

			const response = await fetch(
				`/api/game/maerchenweber/session/${sessionIdToLoad}`,
			);

			if (!response.ok) {
				throw new Error("Session not found");
			}

			const session = await response.json();

			// Extract session data
			sessionId = sessionIdToLoad;
			characterName = session.character_name;
			characterDescription = session.character_description;
			storyTheme = session.story_theme;
			round = session.round || 1;

			// Get the last story and image from history
			const history = session.history || [];
			if (history.length > 0) {
				// Last non-choice item is the latest story
				currentStory = history[history.length - 1];
			}

			// Get current image from image_history
			const imageHistory = session.image_history || [];
			if (imageHistory.length > 0) {
				currentImageUrl = imageHistory[imageHistory.length - 1].url;
			}

			// Show a "continue" state - we need to generate new choices
			// For now, we'll need the user to make a dummy choice to get new options
			// Or we could call a special "resume" endpoint
			// For simplicity, let's show the last story and allow them to continue

			// Generate choices for the current state
			// We'll create a simple continue button that makes a dummy turn
			gamePhase = "playing";

			// Set placeholder choices - user will click "Continue Story" to generate real choices
			currentChoices = ["Geschichte fortsetzen..."];

			console.log(`Loaded session ${sessionId} at round ${round}`);
		} catch (error) {
			console.error("Error loading session:", error);
			alert(
				"Fehler beim Laden der Geschichte. Bitte versuche es erneut.",
			);
			goto("/");
		} finally {
			loading = false;
		}
	}

	async function startAdventure() {
		if (
			!characterName.trim() ||
			!characterDescription.trim() ||
			!storyTheme.trim()
		) {
			alert("Bitte fülle alle Felder aus!");
			return;
		}

		loading = true;
		isStarting = true;
		gamePhase = "loading";

		try {
			lastError = null;
			lastTiming = null;
			warnings = [];

			const response = await fetch("/api/game/maerchenweber/start", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					user_id: userId,
					character_name: characterName,
					character_description: characterDescription,
					story_theme: storyTheme,
				}),
			});

			const data = await response.json();

			if (!response.ok) {
				// Detailed error from backend
				lastError = {
					message: data.error || "Failed to start adventure",
					step: data.step || "Unknown",
					details: data.details || {},
					statusCode: response.status,
				};
				console.error("Adventure start error:", lastError);
				alert(
					`Fehler beim Starten des Abenteuers.\n\nSchritt: ${lastError.step}\nDetails: ${lastError.message}`,
				);
				gamePhase = "setup";
				return;
			}

			// Success! Extract data and timing
			sessionId = data.session_id;
			currentStory = data.step.story_text;
			currentImageUrl = data.step.image_url;
			currentChoices = data.step.choices;
			funNugget = data.step.fun_nugget || "";
			choicesHistory = data.step.choices_history || [];
			round = data.step.round_number || 1;
			lastTiming = data.step.timing || null;
			warnings = data.step.warnings || [];

			if (debugMode && lastTiming) {
				console.log("⏱️ Timing:", lastTiming);
			}
			if (warnings.length > 0) {
				console.warn("⚠️ Warnings:", warnings);
			}

			gamePhase = "playing";
		} catch (error) {
			console.error("Error starting adventure:", error);
			lastError = {
				message:
					error instanceof Error ? error.message : "Unknown error",
				step: "Network/Client",
				details: { type: "ClientError" },
				statusCode: 0,
			};
			alert(
				"Fehler beim Starten des Abenteuers. Bitte versuche es erneut.",
			);
			gamePhase = "setup";
		} finally {
			loading = false;
			isStarting = false;
		}
	}

	async function pollForImage(sessionIdToPoll: string, roundToPoll: number) {
		// Clear any existing polls
		if (pollInterval) clearInterval(pollInterval);
		if (pollTimeout) clearTimeout(pollTimeout);

		imageLoading = true;
		imageError = false;
		imageErrorMessage = "";
		currentImageUrl = null;

		let pollAttempts = 0;
		const maxAttempts = 15; // 15 attempts * 2s = 30s

		// Poll every 2 seconds
		pollInterval = setInterval(async () => {
			pollAttempts++;

			try {
				const response = await fetch(
					`/api/game/maerchenweber/image/${sessionIdToPoll}/${roundToPoll}`,
				);

				if (!response.ok) {
					const error = await response.json();
					throw new Error(
						error.user_message ||
							error.error ||
							"Fehler beim Laden des Bildes",
					);
				}

				const data = await response.json();

				if (data.status === "ready" && data.image_url) {
					currentImageUrl = data.image_url;
					imageLoading = false;
					if (pollInterval) clearInterval(pollInterval);
					if (pollTimeout) clearTimeout(pollTimeout);
					console.log(`✅ Image loaded after ${pollAttempts} attempts`);
				} else if (data.status === "failed") {
					imageError = true;
					imageErrorMessage =
						data.user_message ||
						data.error ||
						"Bildgenerierung fehlgeschlagen";
					imageRetryAfter = data.retry_after || 5;
					imageLoading = false;
					if (pollInterval) clearInterval(pollInterval);
					if (pollTimeout) clearTimeout(pollTimeout);
					console.error("Image generation failed:", data.error);
				}

				// Stop polling after max attempts
				if (pollAttempts >= maxAttempts && imageLoading) {
					imageError = true;
					imageErrorMessage =
						"Zeitüberschreitung: Das Bild konnte nicht geladen werden.";
					imageLoading = false;
					if (pollInterval) clearInterval(pollInterval);
					if (pollTimeout) clearTimeout(pollTimeout);
				}
			} catch (error) {
				console.error("Error polling for image:", error);
				imageError = true;
				imageErrorMessage =
					error instanceof Error
						? error.message
						: "Fehler beim Laden des Bildes";
				imageLoading = false;
				if (pollInterval) clearInterval(pollInterval);
				if (pollTimeout) clearTimeout(pollTimeout);
			}
		}, 2000);
	}

	async function makeChoice(choiceText: string) {
		// Show loading state temporarily
		loading = true;

		// Optimistically add the choice to history for immediate display during loading
		choicesHistory = [...choicesHistory, choiceText];

		try {
			const response = await fetch("/api/game/maerchenweber/turn", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					session_id: sessionId,
					choice_text: choiceText,
				}),
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.error || "Failed to process turn");
			}

			const data = await response.json();

			// Update story and choices IMMEDIATELY (before image)
			currentStory = data.story_text;
			currentChoices = data.choices;
			funNugget = data.fun_nugget || "";
			choicesHistory = data.choices_history || []; // Server response includes the same choice
			round = data.round_number || round + 1;

			// Stop loading state NOW - story is visible
			loading = false;

			// Handle image (async for rounds 2+)
			if (data.image_url) {
				// Round 1: image included in response
				currentImageUrl = data.image_url;
			} else {
				// Rounds 2+: start polling for image
				pollForImage(sessionId, round);
			}
		} catch (error) {
			console.error("Error processing turn:", error);

			// Revert the optimistic update on error
			choicesHistory = choicesHistory.slice(0, -1);
			loading = false;

			// Show user-friendly error message
			if (error instanceof Error) {
				errorMessage = error.message;
			} else {
				errorMessage =
					"Fehler beim Verarbeiten deiner Wahl. Bitte versuche es erneut.";
			}
			showError = true;

			// Auto-hide error after 5 seconds
			setTimeout(() => {
				showError = false;
			}, 5000);
		}
	}

	function retryImageGeneration() {
		pollForImage(sessionId, round);
	}

	function returnHome() {
		goto("/");
	}
</script>

<svelte:head>
	<title>Märchenweber - Kinder Denkspiele</title>
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400"
>
	<div class="container mx-auto p-4 md:p-8 max-w-4xl">
		<!-- Header -->
		<div class="flex justify-between items-center mb-6">
			<h1
				class="text-3xl md:text-4xl font-black text-amber-900 flex items-center gap-2"
			>
				📖 Märchenweber
			</h1>
			<Button variant="secondary" onclick={returnHome}>← Zurück</Button>
		</div>

		{#if gamePhase === "setup"}
			<!-- Setup Phase -->
			<Card>
				<div class="space-y-6">
					<div class="text-center mb-8">
						<h2
							class="text-2xl md:text-3xl font-bold text-gray-800 mb-2"
						>
							Erzähle deine Geschichte!
						</h2>
						<p class="text-gray-600">
							Erstelle deinen Charakter und beginne ein magisches
							Abenteuer
						</p>
					</div>

					<div class="space-y-4">
						<div>
							<label
								for="characterName"
								class="block text-lg font-semibold text-gray-700 mb-2"
							>
								Wie heißt dein Charakter?
							</label>
							<input
								id="characterName"
								type="text"
								bind:value={characterName}
								placeholder="z.B. Prinzessin Luna"
								class="w-full px-4 py-3 text-lg border-2 border-amber-300 rounded-lg focus:outline-none focus:border-amber-500 bg-white"
								maxlength="100"
							/>
						</div>

						<div>
							<label
								for="characterDescription"
								class="block text-lg font-semibold text-gray-700 mb-2"
							>
								Beschreibe deinen Charakter
							</label>
							<input
								id="characterDescription"
								type="text"
								bind:value={characterDescription}
								placeholder="z.B. eine mutige Prinzessin mit magischen Kräften"
								class="w-full px-4 py-3 text-lg border-2 border-amber-300 rounded-lg focus:outline-none focus:border-amber-500 bg-white"
								maxlength="200"
							/>
						</div>

						<div>
							<label
								for="storyTheme"
								class="block text-lg font-semibold text-gray-700 mb-2"
							>
								Wo spielt die Geschichte?
							</label>
							<input
								id="storyTheme"
								type="text"
								bind:value={storyTheme}
								placeholder="z.B. in einem verzauberten Wald"
								class="w-full px-4 py-3 text-lg border-2 border-amber-300 rounded-lg focus:outline-none focus:border-amber-500 bg-white"
								maxlength="200"
							/>
						</div>
					</div>

					<div class="text-center mt-8">
						<Button
							variant="primary"
							onclick={startAdventure}
							class="px-8 py-4 text-xl"
						>
							✨ Abenteuer beginnen
						</Button>
					</div>
				</div>
			</Card>
		{:else if gamePhase === "loading"}
			<!-- Loading Phase with Engagement -->
			<div class="space-y-4">
				<!-- Journey Recap (if there are previous choices) -->
				<JourneyRecap choices={choicesHistory} />

				<!-- Fun Nugget (if generated) -->
				{#if funNugget}
					<FunNuggetCard text={funNugget} />
				{/if}

				<!-- Progress Steps -->
				<ProgressSteps {isStarting} />
			</div>
		{:else if gamePhase === "playing"}
			<!-- Playing Phase -->
			<div class="space-y-6">
				<!-- Round counter -->
				<div class="text-center">
					<span
						class="inline-block bg-amber-200 px-4 py-2 rounded-full text-sm font-semibold text-amber-900"
					>
						Runde {round}
					</span>
				</div>

				<!-- Story Image -->
				{#if imageLoading}
					<!-- Image loading state -->
					<Card>
						<div
							class="w-full h-64 md:h-96 flex flex-col items-center justify-center bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg"
						>
							<div class="text-6xl mb-4 animate-bounce">🎨</div>
							<p class="text-xl md:text-2xl font-semibold text-amber-900">
								Dein Bild wird gemalt...
							</p>
							<p class="text-sm text-amber-700 mt-2">
								Dies kann ein paar Sekunden dauern
							</p>
						</div>
					</Card>
				{:else if imageError}
					<!-- Image error state -->
					<Card>
						<div
							class="w-full h-64 md:h-96 flex flex-col items-center justify-center bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-6"
						>
							<div class="text-6xl mb-4">⚠️</div>
							<p
								class="text-xl md:text-2xl font-semibold text-red-900 mb-2 text-center"
							>
								{imageErrorMessage ||
									"Bildgenerierung fehlgeschlagen"}
							</p>
							<p class="text-sm text-red-700 mb-4 text-center">
								Die Geschichte geht trotzdem weiter!
							</p>
							<Button
								variant="primary"
								onclick={retryImageGeneration}
							>
								🔄 Erneut versuchen
							</Button>
							<p class="text-xs text-red-600 mt-2">
								Warte {imageRetryAfter} Sekunden vor dem
								nächsten Versuch
							</p>
						</div>
					</Card>
				{:else if currentImageUrl}
					<!-- Image ready state -->
					<Card>
						{#key currentImageUrl}
							<img
								src={currentImageUrl}
								alt="Geschichtsbild"
								class="w-full h-64 md:h-96 object-cover rounded-lg"
								loading="eager"
							/>
						{/key}
					</Card>
				{/if}

				<!-- Story Text -->
				<Card>
					<div class="prose prose-lg max-w-none">
						<p
							class="text-xl md:text-2xl leading-relaxed text-gray-800 whitespace-pre-wrap"
						>
							{currentStory}
						</p>
					</div>
				</Card>

				<!-- Choices -->
				{#if !loading}
					<div class="grid gap-4">
						{#each currentChoices as choice, index}
							<button
								onclick={() => makeChoice(choice)}
								class="group relative overflow-hidden bg-white border-3 border-amber-300 rounded-xl p-6 text-left transition-all hover:border-amber-500 hover:shadow-lg hover:-translate-y-1 active:translate-y-0"
							>
								<div class="flex items-start gap-4">
									<span
										class="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full text-xl font-bold"
										class:bg-red-100={index === 0}
										class:text-red-700={index === 0}
										class:bg-blue-100={index === 1}
										class:text-blue-700={index === 1}
										class:bg-green-100={index === 2}
										class:text-green-700={index === 2}
									>
										{index === 0
											? "💪"
											: index === 1
												? "😄"
												: "🤔"}
									</span>
									<span
										class="flex-1 text-lg md:text-xl font-medium text-gray-800"
									>
										{choice}
									</span>
								</div>
							</button>
						{/each}
					</div>
				{:else}
					<!-- Loading during choice selection -->
					<div class="space-y-4">
						<!-- Journey Recap -->
						<JourneyRecap choices={choicesHistory} />

						<!-- Fun Nugget (from previous turn, will update when loaded) -->
						{#if funNugget}
							<FunNuggetCard text={funNugget} />
						{/if}

						<!-- Progress Steps -->
						<ProgressSteps isStarting={false} />
					</div>
				{/if}

				<!-- End Story Button -->
				<div class="text-center mt-8">
					<Button variant="secondary" onclick={returnHome}>
						Geschichte beenden und zurück
					</Button>
				</div>
			</div>
		{/if}

		<!-- Error Toast (Top-center) -->
		{#if showError}
			<div
				class="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 max-w-md"
			>
				<div
					class="bg-red-500 text-white px-6 py-4 rounded-lg shadow-2xl flex items-center gap-3 animate-bounce"
				>
					<span class="text-2xl">⚠️</span>
					<div>
						<p class="font-semibold">Fehler</p>
						<p class="text-sm">{errorMessage}</p>
					</div>
					<button
						onclick={() => (showError = false)}
						class="ml-auto text-white hover:text-red-200"
					>
						✕
					</button>
				</div>
			</div>
		{/if}

		<!-- Debug Panel (Bottom-right floating) -->
		<div class="fixed bottom-4 right-4 z-50">
			<!-- Toggle Button -->
			<button
				onclick={() => (debugMode = !debugMode)}
				class="bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-gray-700 text-sm font-mono"
				title="Toggle debug info"
			>
				{debugMode ? "🐛 Hide Debug" : "🐛 Debug"}
			</button>

			<!-- Debug Info Panel -->
			{#if debugMode}
				<div
					class="mt-2 bg-gray-900 text-gray-100 rounded-lg shadow-2xl p-4 max-w-md max-h-96 overflow-auto text-xs font-mono"
				>
					<h3 class="text-sm font-bold mb-2 text-amber-400">
						🐛 Debug Info
					</h3>

					<!-- Timing Info -->
					{#if lastTiming}
						<div class="mb-4">
							<h4
								class="text-xs font-semibold text-green-400 mb-1"
							>
								⏱️ Last Request Timing
							</h4>
							<div class="bg-gray-800 p-2 rounded">
								<div class="text-yellow-300">
									Total: <span class="font-bold"
										>{lastTiming.total_ms}ms</span
									>
								</div>
								<div class="mt-2 space-y-1">
									{#each lastTiming.steps as step}
										<div
											class="flex justify-between"
											class:text-red-400={step.status ===
												"error"}
											class:text-green-300={step.status ===
												"success"}
										>
											<span>{step.name}</span>
											<span class="font-bold"
												>{step.duration_ms}ms</span
											>
										</div>
										{#if step.error}
											<div
												class="text-red-300 text-xs ml-2"
											>
												Error: {step.error}
											</div>
										{/if}
									{/each}
								</div>
							</div>
						</div>
					{/if}

					<!-- Warnings -->
					{#if warnings.length > 0}
						<div class="mb-4">
							<h4
								class="text-xs font-semibold text-yellow-400 mb-1"
							>
								⚠️ Warnings
							</h4>
							<div
								class="bg-yellow-900 bg-opacity-30 p-2 rounded text-yellow-200"
							>
								{#each warnings as warning}
									<div>• {warning}</div>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Last Error -->
					{#if lastError}
						<div class="mb-4">
							<h4 class="text-xs font-semibold text-red-400 mb-1">
								❌ Last Error
							</h4>
							<div
								class="bg-red-900 bg-opacity-30 p-2 rounded text-red-200"
							>
								<div>
									<strong>Step:</strong>
									{lastError.step}
								</div>
								<div>
									<strong>Status:</strong>
									{lastError.statusCode}
								</div>
								<div>
									<strong>Message:</strong>
									{lastError.message}
								</div>
								{#if lastError.details}
									<div class="mt-1 text-xs">
										<strong>Details:</strong>
										<pre
											class="mt-1 bg-black bg-opacity-30 p-1 rounded overflow-auto">{JSON.stringify(
												lastError.details,
												null,
												2,
											)}</pre>
									</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Session Info -->
					<div class="text-gray-400 text-xs">
						<div>Session: {sessionId || "None"}</div>
						<div>Round: {round}</div>
						<div>Phase: {gamePhase}</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.prose {
		max-width: none;
	}
</style>
