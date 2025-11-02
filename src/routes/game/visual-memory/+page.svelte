<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import GameStats from "$lib/components/GameStats.svelte";
    import VisualMemoryGrid from "$lib/components/VisualMemoryGrid.svelte";
    import type { User } from "$lib/types";

    type GamePhase =
        | "loading"
        | "countdown"
        | "showing"
        | "memorizing"
        | "recalling"
        | "feedback"
        | "gameover";

    let userId = $state("");
    let difficulty = $state<"easy" | "hard" | "extra-hard">("easy");
    let user = $state<User | undefined>(undefined);
    let sessionId = $state<string | null>(null);

    let phase = $state<GamePhase>("loading");
    let score = $state(0);
    let lives = $state(3);
    let round = $state(1);

    let gridSize = $state(3);
    let targetPositions = $state<number[]>([]);
    let userSelections = $state<number[]>([]);
    let feedbackTargets = $state<number[]>([]);
    let presentationTime = $state(2000);
    let retentionDelay = $state(1000);

    let countdown = $state(3);
    let message = $state<string | null>(null);
    let isCorrect = $state<boolean | null>(null);

    onMount(async () => {
        const params = new URLSearchParams(window.location.search);
        userId = params.get("userId") || "";
        difficulty = (params.get("difficulty") as "easy" | "hard" | "extra-hard") || "easy";

        if (!userId) {
            goto("/");
            return;
        }

        try {
            const userResponse = await fetch(`/api/users/${userId}`);
            if (userResponse.ok) {
                user = await userResponse.json();
            }
        } catch (error) {
            console.error("Failed to load user:", error);
        }

        startGame();
    });

    async function startGame() {
        phase = "loading";
        isCorrect = null;
        message = null;

        try {
            const response = await fetch("/api/game/visual-memory/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ userId, difficulty }),
            });

            const data = await response.json();
            sessionId = data.sessionId;
            score = data.score;
            lives = data.lives;
            round = data.round;
            gridSize = data.visualMemoryState.gridSize;
            targetPositions = data.visualMemoryState.targetPositions;
            presentationTime = data.visualMemoryState.presentationTime;
            retentionDelay = data.visualMemoryState.retentionDelay;
            userSelections = [];

            startCountdown();
        } catch (error) {
            console.error("Failed to start game:", error);
            message = "Fehler beim Starten des Spiels";
        }
    }

    function startCountdown() {
        phase = "countdown";
        countdown = 3;

        const interval = setInterval(() => {
            countdown--;
            if (countdown === 0) {
                clearInterval(interval);
                showTargets();
            }
        }, 1000);
    }

    function showTargets() {
        phase = "showing";

        setTimeout(() => {
            memorizePhase();
        }, presentationTime);
    }

    function memorizePhase() {
        phase = "memorizing";

        setTimeout(() => {
            recallPhase();
        }, retentionDelay);
    }

    function recallPhase() {
        phase = "recalling";
        userSelections = [];
        message = null;
    }

    function handleSquareClick(index: number) {
        if (phase !== "recalling") return;

        if (userSelections.includes(index)) {
            userSelections = userSelections.filter((i) => i !== index);
        } else {
            userSelections = [...userSelections, index];
        }
    }

    async function submitAnswer() {
        if (userSelections.length === 0) {
            message = "Bitte wähle mindestens ein Quadrat!";
            return;
        }

        phase = "feedback";
        message = null;

        try {
            const response = await fetch("/api/game/visual-memory/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sessionId, userSelections }),
            });

            const data = await response.json();

            isCorrect = data.isCorrect;
            feedbackTargets = data.previousTargets;

            if (data.gameOver) {
                setTimeout(() => {
                    phase = "gameover";
                    score = data.score;
                    lives = data.lives;
                }, 2500);
            } else {
                score = data.score;
                lives = data.lives;
                round = data.round;
                targetPositions = data.visualMemoryState.targetPositions;

                setTimeout(() => {
                    isCorrect = null;
                    startCountdown();
                }, 2500);
            }
        } catch (error) {
            console.error("Failed to submit answer:", error);
            message = "Fehler beim Senden der Antwort";
        }
    }

    const gridMode = $derived<
        "showing" | "memorizing" | "recalling" | "feedback"
    >(
        phase === "showing"
            ? "showing"
            : phase === "memorizing"
              ? "memorizing"
              : phase === "recalling"
                ? "recalling"
                : phase === "feedback"
                  ? "feedback"
                  : "memorizing",
    );
</script>

<svelte:head>
    <title>Visuelles Gedächtnis - Kinder Denkspiele</title>
</svelte:head>

<svelte:window
    ontouchstart={(e) => {
        if (e.touches.length > 1) {
            e.preventDefault();
        }
    }}
    ontouchmove={(e) => {
        if (e.touches.length > 1) {
            e.preventDefault();
        }
    }}
/>

<div
    class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-2 animate-gradient"
    style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto;"
>
    <div class="max-w-4xl mx-auto pt-14">
        <Card class="mb-2 py-3">
            <GameStats {score} {lives} {round} {user} />
        </Card>

        {#if phase === "loading"}
            <Card>
                <div class="text-center py-12">
                    <p class="text-2xl font-bold text-gray-700">
                        Spiel wird geladen...
                    </p>
                </div>
            </Card>
        {:else if phase === "countdown"}
            <Card>
                <div class="text-center py-16 animate-fade-in">
                    <p
                        class="text-8xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent animate-pulse"
                    >
                        {countdown}
                    </p>
                    <p class="text-2xl font-bold text-gray-700 mt-4">
                        Mach dich bereit!
                    </p>
                </div>
            </Card>
        {:else if phase === "gameover"}
            <Card>
                <div class="text-center py-8 animate-fade-in">
                    <div class="mb-4">
                        <span class="text-6xl inline-block animate-bounce-slow"
                            >🎮</span
                        >
                    </div>
                    <h2
                        class="text-4xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4"
                    >
                        Spiel vorbei!
                    </h2>
                    <div
                        class="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-2xl p-6 mb-4 border-4 border-yellow-300"
                    >
                        <p class="text-xl text-gray-700 font-bold mb-1">
                            Deine Punktzahl
                        </p>
                        <p
                            class="text-6xl font-black bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent"
                        >
                            {score}
                        </p>
                    </div>
                    <p class="text-xl text-gray-600 font-semibold mb-6">
                        Schwierigkeit: {difficulty === "easy"
                            ? "🟢 Einfach"
                            : difficulty === "hard"
                              ? "🔴 Schwer"
                              : "🟣 Extra Schwer"}
                    </p>
                    <div class="flex gap-4 justify-center flex-wrap">
                        <Button variant="success" size="lg" onclick={startGame}>
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🔄</span>
                                <span>Nochmal spielen</span>
                            </div>
                        </Button>
                        <Button
                            variant="secondary"
                            size="lg"
                            onclick={() => goto("/")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🏠</span>
                                <span>Zur Startseite</span>
                            </div>
                        </Button>
                    </div>
                </div>
            </Card>
        {:else}
            <Card>
                <div class="py-3">
                    <!-- Fixed height instruction area to prevent shifts -->
                    <div class="h-16 flex flex-col items-center justify-center mb-3">
                        {#if phase === "showing"}
                            <p class="text-lg font-bold text-center text-gray-700 animate-fade-in">
                                Merke dir die <span class="text-blue-600">blauen</span> Quadrate!
                            </p>
                        {:else if phase === "memorizing"}
                            <p class="text-lg font-bold text-center text-gray-700 mb-2 animate-fade-in">
                                Warte kurz... 🧠
                            </p>
                            <div class="w-full max-w-md mx-auto">
                                <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        class="h-full bg-gradient-to-r from-purple-500 to-pink-500 animate-progress"
                                        style="animation-duration: {retentionDelay}ms;"
                                    ></div>
                                </div>
                            </div>
                        {:else if phase === "recalling"}
                            <p class="text-lg font-bold text-center text-gray-700 animate-fade-in">
                                Welche Quadrate waren blau?
                            </p>
                        {:else if phase === "feedback"}
                            <p class="text-lg font-bold text-center animate-fade-in {isCorrect ? 'text-green-600' : 'text-red-600'}">
                                {isCorrect ? "✓ Richtig! Super! 🎉" : "✗ Nicht ganz richtig... 😔"}
                            </p>
                        {/if}
                    </div>

                    <VisualMemoryGrid
                        {gridSize}
                        targetPositions={phase === "feedback"
                            ? feedbackTargets
                            : targetPositions}
                        {userSelections}
                        mode={gridMode}
                        onSquareClick={handleSquareClick}
                        disabled={phase !== "recalling"}
                    />

                    <!-- Fixed height button area to prevent shifts -->
                    <div class="mt-3 text-center h-20 flex flex-col items-center justify-center">
                        {#if phase === "recalling"}
                            {#if message}
                                <p class="text-red-600 font-bold mb-2 text-sm">
                                    {message}
                                </p>
                            {/if}
                            <Button
                                variant="primary"
                                size="md"
                                onclick={submitAnswer}
                                disabled={userSelections.length === 0}
                            >
                                <div class="flex items-center gap-1">
                                    <span class="text-xl">✓</span>
                                    <span>Bestätigen ({userSelections.length})</span>
                                </div>
                            </Button>
                        {/if}
                    </div>
                </div>
            </Card>
        {/if}
    </div>
</div>

<style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes bounceSlow {
        0%,
        100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-20px);
        }
    }

    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    .animate-fade-in {
        animation: fadeIn 0.8s ease-out;
    }

    .animate-bounce-slow {
        animation: bounceSlow 3s ease-in-out infinite;
    }

    .animate-gradient {
        background-size: 200% 200%;
        animation: gradient 15s ease infinite;
    }

    .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    @keyframes progress {
        from {
            width: 0%;
        }
        to {
            width: 100%;
        }
    }

    .animate-progress {
        animation: progress linear;
        animation-fill-mode: forwards;
    }
</style>
