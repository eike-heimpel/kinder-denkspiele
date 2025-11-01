<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import type { User } from "$lib/types";

    type GamePhase =
        | "loading"
        | "instructions"
        | "wait"
        | "ready"
        | "result"
        | "gameover";

    let userId = $state("");
    let difficulty = $state<"easy" | "hard">("easy");
    let user = $state<User | undefined>(undefined);
    let sessionId = $state<string | null>(null);

    let phase = $state<GamePhase>("loading");
    let currentRound = $state(1);
    let totalRounds = $state(5);
    let reactionTimes = $state<number[]>([]);
    let currentReactionTime = $state(0);
    let averageTime = $state(0);
    let bestTime = $state(0);
    let falseStarts = $state(0);

    let startTime = $state(0);
    let minDelay = $state(2000);
    let maxDelay = $state(4000);
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    onMount(async () => {
        const params = new URLSearchParams(window.location.search);
        userId = params.get("userId") || "";
        difficulty = (params.get("difficulty") as "easy" | "hard") || "easy";

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
        try {
            const response = await fetch("/api/game/reaction-time/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ userId, difficulty }),
            });

            const data = await response.json();
            sessionId = data.sessionId;
            currentRound = data.reactionTimeState.currentRound;
            totalRounds = data.reactionTimeState.totalRounds;
            reactionTimes = data.reactionTimeState.reactionTimes;
            minDelay = data.reactionTimeState.minDelay;
            maxDelay = data.reactionTimeState.maxDelay;
            falseStarts = data.reactionTimeState.falseStarts;

            phase = "instructions";
        } catch (error) {
            console.error("Failed to start game:", error);
        }
    }

    function startRound() {
        phase = "wait";
        const delay = generateDelay(minDelay, maxDelay);

        timeoutId = setTimeout(() => {
            phase = "ready";
            startTime = Date.now();
        }, delay);
    }

    function generateDelay(min: number, max: number): number {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    async function handleClick() {
        if (phase === "wait") {
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
            await submitFalseStart();
        } else if (phase === "ready") {
            const reactionTime = Date.now() - startTime;
            currentReactionTime = reactionTime;
            await submitReaction(reactionTime);
        }
    }

    async function submitReaction(reactionTime: number) {
        phase = "result";

        try {
            const response = await fetch("/api/game/reaction-time/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sessionId,
                    reactionTime,
                    isFalseStart: false,
                }),
            });

            const data = await response.json();

            if (data.gameOver) {
                reactionTimes = data.reactionTimeState.reactionTimes;
                averageTime = data.score;
                bestTime = Math.min(...reactionTimes);
                phase = "gameover";
            } else {
                currentRound = data.reactionTimeState.currentRound;
                reactionTimes = data.reactionTimeState.reactionTimes;
            }
        } catch (error) {
            console.error("Failed to submit reaction:", error);
        }
    }

    async function submitFalseStart() {
        phase = "result";
        currentReactionTime = -1;

        try {
            const response = await fetch("/api/game/reaction-time/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sessionId,
                    isFalseStart: true,
                }),
            });

            const data = await response.json();
            falseStarts = data.reactionTimeState.falseStarts;
            currentRound = data.reactionTimeState.currentRound;
        } catch (error) {
            console.error("Failed to submit false start:", error);
        }
    }

    function nextRound() {
        startRound();
    }
</script>

<svelte:head>
    <title>Reaktionszeit - Kinder Denkspiele</title>
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
    class="min-h-screen bg-gradient-to-br from-orange-500 via-red-500 to-pink-500 p-2"
    style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto;"
>
    <div class="max-w-4xl mx-auto pt-14">
        {#if phase === "loading"}
            <Card>
                <div class="text-center py-12">
                    <p class="text-2xl font-bold text-gray-700">
                        Spiel wird geladen...
                    </p>
                </div>
            </Card>
        {:else if phase === "instructions"}
            <div class="text-center mb-4 animate-fade-in">
                <span class="text-5xl inline-block mb-2 animate-bounce-slow"
                    >⚡</span
                >
                <h1
                    class="text-4xl font-black text-white drop-shadow-2xl tracking-tight"
                >
                    Reaktionszeit
                </h1>
            </div>

            <Card>
                <div class="text-center py-8">
                    <h2
                        class="text-3xl font-black bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-6"
                    >
                        Wie schnell bist du?
                    </h2>

                    <div class="space-y-4 text-left max-w-md mx-auto mb-8">
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">⏳</span>
                            <p class="text-lg text-gray-700">
                                Warte auf den <span
                                    class="text-red-600 font-bold">roten</span
                                > Bildschirm
                            </p>
                        </div>
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">👀</span>
                            <p class="text-lg text-gray-700">
                                Sei bereit, wenn es <span
                                    class="text-green-600 font-bold">grün</span
                                > wird
                            </p>
                        </div>
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">👆</span>
                            <p class="text-lg text-gray-700">
                                Tippe so schnell wie möglich!
                            </p>
                        </div>
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">⚠️</span>
                            <p class="text-lg text-gray-700">
                                Nicht zu früh klicken!
                            </p>
                        </div>
                    </div>

                    <div class="mb-4">
                        <p class="text-xl text-gray-600 font-semibold">
                            Runden: {totalRounds}
                        </p>
                        <p class="text-xl text-gray-600 font-semibold">
                            Schwierigkeit: {difficulty === "easy"
                                ? "🟢 Einfach"
                                : "🔴 Schwer"}
                        </p>
                    </div>

                    <Button variant="success" size="lg" onclick={startRound}>
                        <div class="flex items-center gap-2">
                            <span class="text-3xl">🚀</span>
                            <span>Los geht's!</span>
                        </div>
                    </Button>
                </div>
            </Card>
        {:else if phase === "wait"}
            <button
                class="fixed inset-0 bg-red-500 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 active:bg-red-600"
                onclick={handleClick}
            >
                <p class="text-6xl font-black text-white drop-shadow-2xl mb-4">
                    Warte...
                </p>
                <p class="text-2xl text-white/90 font-bold">
                    Runde {currentRound} von {totalRounds}
                </p>
            </button>
        {:else if phase === "ready"}
            <button
                class="fixed inset-0 bg-green-500 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 active:bg-green-600"
                onclick={handleClick}
            >
                <p
                    class="text-6xl font-black text-white drop-shadow-2xl mb-4 animate-pulse"
                >
                    JETZT!
                </p>
                <p class="text-3xl text-white font-bold">👆 Tippe!</p>
            </button>
        {:else if phase === "result"}
            <div class="text-center mb-4 animate-fade-in">
                <span class="text-5xl inline-block mb-2">⚡</span>
                <h1 class="text-4xl font-black text-white drop-shadow-2xl">
                    Reaktionszeit
                </h1>
            </div>

            <Card>
                <div class="text-center py-8">
                    {#if currentReactionTime === -1}
                        <div class="mb-6">
                            <span class="text-6xl inline-block mb-4">⚠️</span>
                            <h2
                                class="text-4xl font-black bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-4"
                            >
                                Zu früh!
                            </h2>
                            <p class="text-xl text-gray-700 font-semibold">
                                Warte bis es grün wird!
                            </p>
                        </div>
                    {:else}
                        <div class="mb-6">
                            <span class="text-6xl inline-block mb-4">⚡</span>
                            <h2
                                class="text-4xl font-black bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-4"
                            >
                                {currentReactionTime}ms
                            </h2>
                            <p class="text-xl text-gray-700 font-semibold">
                                {#if currentReactionTime < 200}
                                    🚀 Blitzschnell!
                                {:else if currentReactionTime < 300}
                                    ⚡ Sehr gut!
                                {:else if currentReactionTime < 400}
                                    👍 Gut!
                                {:else}
                                    💪 Weiter üben!
                                {/if}
                            </p>
                        </div>
                    {/if}

                    <div
                        class="bg-gray-50 rounded-xl p-4 mb-6 max-w-md mx-auto"
                    >
                        <p class="text-sm text-gray-600 mb-2">
                            Runde {currentRound - 1} von {totalRounds}
                        </p>
                        <div class="flex justify-center gap-2">
                            {#each Array(totalRounds) as _, i}
                                <div
                                    class="w-8 h-8 rounded-lg {i <
                                    reactionTimes.length
                                        ? 'bg-green-500'
                                        : 'bg-gray-300'}"
                                ></div>
                            {/each}
                        </div>
                    </div>

                    {#if currentRound <= totalRounds}
                        <Button variant="primary" size="lg" onclick={nextRound}>
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">➡️</span>
                                <span>Nächste Runde</span>
                            </div>
                        </Button>
                    {/if}
                </div>
            </Card>
        {:else if phase === "gameover"}
            <div class="text-center mb-4 animate-fade-in">
                <span class="text-5xl inline-block mb-2">🏁</span>
                <h1 class="text-4xl font-black text-white drop-shadow-2xl">
                    Fertig!
                </h1>
            </div>

            <Card>
                <div class="text-center py-8">
                    <div class="mb-6">
                        <h2 class="text-2xl font-bold text-gray-700 mb-4">
                            Deine Ergebnisse
                        </h2>

                        <div
                            class="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-2xl p-6 mb-4 border-4 border-yellow-300"
                        >
                            <p class="text-lg text-gray-700 font-bold mb-1">
                                Durchschnitt
                            </p>
                            <p
                                class="text-5xl font-black bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent"
                            >
                                {averageTime}ms
                            </p>
                        </div>

                        <div
                            class="bg-gradient-to-r from-green-100 to-emerald-100 rounded-2xl p-6 mb-4 border-4 border-green-300"
                        >
                            <p class="text-lg text-gray-700 font-bold mb-1">
                                Schnellste
                            </p>
                            <p
                                class="text-5xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent"
                            >
                                {bestTime}ms
                            </p>
                        </div>

                        {#if falseStarts > 0}
                            <div class="bg-red-50 rounded-xl p-4 mb-4">
                                <p class="text-gray-700 font-semibold">
                                    Fehlstarts: {falseStarts}
                                </p>
                            </div>
                        {/if}

                        <div class="flex flex-wrap justify-center gap-2 mb-4">
                            {#each reactionTimes as time, i}
                                <div
                                    class="bg-blue-100 rounded-lg px-3 py-2 border-2 border-blue-300"
                                >
                                    <p class="text-xs text-gray-600">
                                        Runde {i + 1}
                                    </p>
                                    <p class="text-lg font-bold text-blue-700">
                                        {time}ms
                                    </p>
                                </div>
                            {/each}
                        </div>
                    </div>

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
        {/if}

        {#if phase !== "wait" && phase !== "ready"}
            <div class="text-center mt-3">
                <Button variant="secondary" onclick={() => goto("/")}>
                    ← Zurück zur Startseite
                </Button>
            </div>
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

    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }

    .animate-fade-in {
        animation: fadeIn 0.8s ease-out;
    }

    .animate-bounce-slow {
        animation: bounceSlow 3s ease-in-out infinite;
    }

    .animate-pulse {
        animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
</style>
