<script lang="ts">
	import { onMount } from "svelte";
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";
	import Button from "$lib/components/Button.svelte";
	import Card from "$lib/components/Card.svelte";
	import JourneyRecap from "$lib/components/JourneyRecap.svelte";
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
	let previousImages = $state<string[]>([]);
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

	// Choice visibility state
	let showChoices = $state<boolean>(false);

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

			// Extract session metadata
			sessionId = sessionIdToLoad;
			characterName = session.character_name;
			characterDescription = session.character_description;
			storyTheme = session.story_theme;
			round = session.round || 0;

			// Get turns array
			const turns = session.turns || [];

			// Check generation status
			const generationStatus = session.generation_status;

			if (generationStatus === "generating") {
				// Still generating, poll for completion
				gamePhase = "loading";
				await pollForTurnCompletion(sessionIdToLoad);
			} else if (generationStatus === "error") {
				// Generation failed
				alert("Story generation failed. Please start a new story.");
				goto("/game/maerchenweber");
			} else if (turns.length > 0) {
				// Ready - restore from last turn
				const lastTurn = turns[turns.length - 1];

				currentStory = lastTurn.story_text;
				currentChoices = lastTurn.choices || [];
				currentImageUrl = lastTurn.image_url;  // May be null if image failed
				previousImages = [];  // Will be populated on next API call
				round = lastTurn.round;

				// Extract choices history from turns
				choicesHistory = turns
					.map((t: any) => t.choice_made)
					.filter((c: any) => c !== null && c !== undefined);

				// Check if image is still generating
				if (!lastTurn.image_url && session.pending_image?.status === "generating") {
					pollForImage(sessionIdToLoad, round);
				}

				gamePhase = "playing";
				console.log(`Loaded session ${sessionId} at round ${round}`);
			} else {
				// No turns yet (shouldn't happen, but handle gracefully)
				alert("Session has no story data. Please start a new story.");
				goto("/game/maerchenweber");
			}
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

			// Got session_id, now poll for completion
			sessionId = data.session_id;
			console.log(`[Märchenweber] Session created: ${sessionId}, starting polling...`);

			// Poll for story completion
			await pollForStoryCompletion(sessionId);
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

	async function pollForStoryCompletion(sid: string) {
		const maxAttempts = 30; // 30 attempts * 2 seconds = 60 seconds max
		let attempts = 0;

		while (attempts < maxAttempts) {
			try {
				const response = await fetch(`/api/game/maerchenweber/status/${sid}`);
				const data = await response.json();

				console.log(`[Märchenweber] Poll attempt ${attempts + 1}: status=${data.status}`);

				if (data.status === 'ready') {
					// Story is ready!
					currentStory = data.step.story_text;
					currentImageUrl = data.step.image_url;
					currentChoices = data.step.choices;
					previousImages = data.step.previous_images || [];
					choicesHistory = data.step.choices_history || [];
					round = data.step.round_number || 1;
					showChoices = false; // Hide choices initially

					console.log('[Märchenweber] Story ready!');
					gamePhase = "playing";
					return;
				} else if (data.status === 'error') {
					// Generation failed
					lastError = {
						message: data.error || "Story generation failed",
						step: "Generation",
						details: {},
						statusCode: 500,
					};
					alert("Die Geschichte konnte nicht erstellt werden. Bitte versuche es erneut.");
					gamePhase = "setup";
					return;
				}

				// Still generating, wait and retry
				await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
				attempts++;
			} catch (error) {
				console.error(`[Märchenweber] Polling error:`, error);
				attempts++;
				await new Promise(resolve => setTimeout(resolve, 2000));
			}
		}

		// Timeout
		alert("Die Geschichte braucht zu lange. Bitte versuche es erneut.");
		gamePhase = "setup";
	}

	async function pollForTurnCompletion(sid: string) {
		const maxAttempts = 30; // 30 attempts * 2 seconds = 60 seconds max
		let attempts = 0;

		while (attempts < maxAttempts) {
			try {
				const response = await fetch(`/api/game/maerchenweber/status/${sid}`);
				const data = await response.json();

				console.log(`[Märchenweber] Turn poll attempt ${attempts + 1}: status=${data.status}`);

				if (data.status === 'ready') {
					// Story is ready! Get data from status response
					currentStory = data.step.story_text;
					currentChoices = data.step.choices;
					previousImages = data.step.previous_images || [];
					choicesHistory = data.step.choices_history || [];
					round = data.step.round_number || round;
					showChoices = false; // Hide choices initially

					console.log('[Märchenweber] Turn ready!');
					loading = false;
					gamePhase = "playing";

					// Handle image (might be included or need polling)
					if (data.step.image_url) {
						currentImageUrl = data.step.image_url;
					} else {
						// Start polling for image
						pollForImage(sessionId, round);
					}
					return;
				} else if (data.status === 'error') {
					// Generation failed - reload session to get reverted state
					const sessionResponse = await fetch(`/api/game/maerchenweber/session/${sid}`);
					const session = await sessionResponse.json();

					const turns = session.turns || [];
					if (turns.length > 0) {
						const lastTurn = turns[turns.length - 1];
						currentStory = lastTurn.story_text;
						currentChoices = lastTurn.choices;
						currentImageUrl = lastTurn.image_url;
						previousImages = [];  // Will be populated on next API call
						round = lastTurn.round;

						choicesHistory = turns
							.map((t: any) => t.choice_made)
							.filter((c: any) => c !== null && c !== undefined);
					}

					lastError = {
						message: data.error || "Turn generation failed",
						step: "Generation",
						details: {},
						statusCode: 500,
					};
					alert("Die Geschichte konnte nicht fortgesetzt werden. Bitte versuche es erneut.");
					loading = false;
					gamePhase = "playing";
					return;
				}

				// Still generating, wait and retry
				await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
				attempts++;
			} catch (error) {
				console.error(`[Märchenweber] Turn polling error:`, error);
				attempts++;
				await new Promise(resolve => setTimeout(resolve, 2000));
			}
		}

		// Timeout - reload session to get current state
		const sessionResponse = await fetch(`/api/game/maerchenweber/session/${sid}`);
		const session = await sessionResponse.json();

		const turns = session.turns || [];
		if (turns.length > 0) {
			const lastTurn = turns[turns.length - 1];
			currentStory = lastTurn.story_text;
			currentChoices = lastTurn.choices;
			currentImageUrl = lastTurn.image_url;
			previousImages = [];  // Will be populated on next API call
			round = lastTurn.round;

			choicesHistory = turns
				.map((t: any) => t.choice_made)
				.filter((c: any) => c !== null && c !== undefined);
		}

		alert("Die Geschichte braucht zu lange. Bitte versuche es erneut.");
		loading = false;
		gamePhase = "playing";
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
		// Show loading state
		loading = true;
		gamePhase = "loading";

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

			// Check if we got immediate response with generating status
			if (data.status === 'generating') {
				console.log('[Märchenweber] Turn started, polling for completion...');
				// Poll for completion
				await pollForTurnCompletion(sessionId);
			} else {
				// Fallback: old synchronous response (shouldn't happen with new backend)
				currentStory = data.story_text;
				currentChoices = data.choices;
				previousImages = data.previous_images || [];
				choicesHistory = data.choices_history || [];
				round = data.round_number || round + 1;
				showChoices = false; // Hide choices initially

				loading = false;
				gamePhase = "playing";

				// Handle image
				if (data.image_url) {
					currentImageUrl = data.image_url;
				} else {
					pollForImage(sessionId, round);
				}
			}
		} catch (error) {
			console.error("Error processing turn:", error);

			loading = false;
			gamePhase = "playing";

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

				<!-- Previous Images Gallery (if available) -->
				{#if previousImages.length > 0}
					<Card>
						<div class="flex flex-col gap-2">
							<h3 class="text-sm font-semibold text-center text-gray-600 mb-1">
								Deine bisherige Reise
							</h3>
							<div class="flex flex-col gap-2">
								{#each previousImages.slice(-4).reverse() as imageUrl, index}
									<div
										class="relative rounded-md overflow-hidden"
										style="opacity: {1 - (index * 0.15)}; max-height: 120px;"
									>
										<img
											src={imageUrl}
											alt="Szene {previousImages.length - index}"
											class="w-full h-full object-cover rounded-md"
										/>
									</div>
								{/each}
							</div>
						</div>
					</Card>
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
							class="text-2xl md:text-3xl leading-loose tracking-wide text-gray-800 whitespace-pre-wrap"
							style="word-spacing: 0.15em;"
						>
							{currentStory}
						</p>
					</div>
				</Card>

				<!-- Choices -->
				{#if !loading}
					{#if !showChoices}
						<!-- Button to reveal choices -->
						<div class="text-center">
							<Button
								variant="primary"
								onclick={() => showChoices = true}
								class="px-8 py-4 text-xl bg-amber-500 hover:bg-amber-600 shadow-lg"
							>
								📜 Zeige mir meine Auswahlmöglichkeiten
							</Button>
						</div>
					{:else}
						<!-- Choice buttons -->
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
					{/if}
				{:else}
					<!-- Loading during choice selection -->
					<div class="space-y-4">
						<!-- Journey Recap -->
						<JourneyRecap choices={choicesHistory} />

						<!-- Previous Images Gallery (if available) -->
						{#if previousImages.length > 0}
							<Card>
								<div class="flex flex-col gap-2">
									<h3 class="text-sm font-semibold text-center text-gray-600 mb-1">
										Deine bisherige Reise
									</h3>
									<div class="flex flex-col gap-2">
										{#each previousImages.slice(-4).reverse() as imageUrl, index}
											<div
												class="relative rounded-md overflow-hidden"
												style="opacity: {1 - (index * 0.15)}; max-height: 120px;"
											>
												<img
													src={imageUrl}
													alt="Szene {previousImages.length - index}"
													class="w-full h-full object-cover rounded-md"
												/>
											</div>
										{/each}
									</div>
								</div>
							</Card>
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
