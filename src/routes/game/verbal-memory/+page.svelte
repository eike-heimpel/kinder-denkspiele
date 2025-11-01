<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import GameStats from "$lib/components/GameStats.svelte";
    import type { User } from "$lib/types";

    let userId = $state("");
    let difficulty = $state<"easy" | "hard" | "extra-hard">("easy");
    let user = $state<User | undefined>(undefined);
    let sessionId = $state<string | null>(null);
    let currentWord = $state<string | null>(null);
    let score = $state(0);
    let lives = $state(3);
    let round = $state(0);
    let gameOver = $state(false);
    let message = $state<string | null>(null);
    let loading = $state(true);
    let answering = $state(false);

    // Debug info
    let showDebug = $state(false);
    let debugInfo = $state<{
        wordsShown: string[];
        seenWords: string[];
        lastThree: Array<{word: string, wasNew: boolean, userAnswer: string, wasCorrect: boolean}>;
    }>({
        wordsShown: [],
        seenWords: [],
        lastThree: []
    });

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
        loading = true;
        try {
            const response = await fetch("/api/game/verbal-memory/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ userId, difficulty }),
            });

            const data = await response.json();
            sessionId = data.sessionId;
            currentWord = data.currentWord;
            score = data.score;
            lives = data.lives;
            round = data.round || 0;
            gameOver = false;
            message = null;

            // Update debug info
            if (data.debug) {
                debugInfo.wordsShown = data.debug.wordsShown;
                debugInfo.seenWords = data.debug.seenWords;
            }
        } catch (error) {
            console.error("Failed to start game:", error);
            message = "Fehler beim Starten des Spiels";
        } finally {
            loading = false;
        }
    }

    async function submitAnswer(answer: "seen" | "new") {
        if (!sessionId || answering) return;

        answering = true;

        try {
            const response = await fetch("/api/game/verbal-memory/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sessionId, answer }),
            });

            const data = await response.json();

            // Update debug info with last answer
            if (data.debug && currentWord) {
                const wasNew = !debugInfo.seenWords.includes(currentWord);
                const wasCorrect = data.debug.wasCorrect;

                debugInfo.lastThree = [
                    {
                        word: currentWord,
                        wasNew: wasNew,
                        userAnswer: answer,
                        wasCorrect: wasCorrect
                    },
                    ...debugInfo.lastThree
                ].slice(0, 3);

                debugInfo.wordsShown = data.debug.wordsShown;
                debugInfo.seenWords = data.debug.seenWords;
            }

            if (data.gameOver) {
                gameOver = true;
                message = data.message;
                currentWord = null;
            } else {
                currentWord = data.currentWord;
                score = data.score;
                lives = data.lives;
                round = data.round || 0;
            }
        } catch (error) {
            console.error("Failed to submit answer:", error);
            message = "Fehler beim Senden der Antwort";
        } finally {
            answering = false;
        }
    }

    function handleKeyPress(event: KeyboardEvent) {
        if (gameOver || answering || !currentWord) return;

        if (
            event.key === "ArrowLeft" ||
            event.key === "n" ||
            event.key === "N"
        ) {
            submitAnswer("new");
        } else if (
            event.key === "ArrowRight" ||
            event.key === "g" ||
            event.key === "G"
        ) {
            submitAnswer("seen");
        }
    }
</script>

<svelte:window
    onkeydown={handleKeyPress}
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

<svelte:head>
    <title>Verbales Gedächtnis - Kinder Denkspiele</title>
</svelte:head>

<div
    class="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-2 animate-gradient"
    style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto;"
>
    <div class="max-w-4xl mx-auto pt-14">
        <Card class="mb-2 py-3">
            <GameStats {score} {lives} {round} {user} />
        </Card>

        {#if loading}
            <Card>
                <div class="text-center py-12">
                    <p class="text-2xl font-bold text-gray-700">
                        Spiel wird geladen...
                    </p>
                </div>
            </Card>
        {:else if gameOver}
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
        {:else if currentWord}
            <Card>
                <div class="text-center py-4">
                    {#key round}
                        <div class="word-display mb-4">
                            <p
                                class="text-5xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent drop-shadow-lg animate-word-appear"
                            >
                                {currentWord}
                            </p>
                        </div>
                    {/key}

                    <p class="text-base font-semibold text-gray-700 mb-3 animate-fade-in">
                        Hast du dieses Wort schon gesehen?
                    </p>

                    <div class="flex gap-3 justify-center">
                        <Button
                            variant="danger"
                            size="md"
                            onclick={() => submitAnswer("new")}
                            disabled={answering}
                        >
                            <div class="flex flex-col items-center gap-1">
                                <span class="text-2xl">🆕</span>
                                <span class="font-bold">NEU</span>
                                <span class="text-xs opacity-75">(← / N)</span>
                            </div>
                        </Button>
                        <Button
                            variant="success"
                            size="md"
                            onclick={() => submitAnswer("seen")}
                            disabled={answering}
                        >
                            <div class="flex flex-col items-center gap-1">
                                <span class="text-2xl">👀</span>
                                <span class="font-bold">Gesehen</span>
                                <span class="text-xs opacity-75">(→ / G)</span>
                            </div>
                        </Button>
                    </div>
                </div>
            </Card>
        {/if}

        <!-- Debug Panel -->
        <div class="mt-4">
            <button
                class="text-xs text-white/70 hover:text-white underline"
                onclick={() => showDebug = !showDebug}
            >
                {showDebug ? '🔻 Debug ausblenden' : '🔺 Debug anzeigen'}
            </button>

            {#if showDebug}
                <Card class="mt-2 text-xs">
                    <div class="space-y-3">
                        <div>
                            <h3 class="font-bold text-sm mb-1">Letzte 3 Wörter:</h3>
                            {#if debugInfo.lastThree.length === 0}
                                <p class="text-gray-500 italic">Noch keine Antworten</p>
                            {:else}
                                <div class="space-y-1">
                                    {#each debugInfo.lastThree as entry}
                                        <div class="flex items-center gap-2 p-2 bg-gray-50 rounded">
                                            <span class="font-bold">{entry.word}</span>
                                            <span class="text-gray-600">
                                                → war {entry.wasNew ? 'NEU' : 'GESEHEN'}
                                            </span>
                                            <span class="text-gray-600">
                                                → du: {entry.userAnswer === 'new' ? 'NEU' : 'GESEHEN'}
                                            </span>
                                            <span class={entry.wasCorrect ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                                                {entry.wasCorrect ? '✓ Richtig' : '✗ Falsch'}
                                            </span>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>

                        <div>
                            <h3 class="font-bold text-sm mb-1">
                                Alle gezeigten Wörter ({debugInfo.wordsShown.length}):
                            </h3>
                            <div class="max-h-32 overflow-y-auto bg-gray-50 p-2 rounded">
                                <div class="flex flex-wrap gap-1">
                                    {#each debugInfo.wordsShown as word}
                                        <span class="bg-blue-100 px-2 py-1 rounded">{word}</span>
                                    {/each}
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 class="font-bold text-sm mb-1">
                                Gesehene Wörter (Set) ({debugInfo.seenWords.length}):
                            </h3>
                            <div class="max-h-32 overflow-y-auto bg-gray-50 p-2 rounded">
                                <div class="flex flex-wrap gap-1">
                                    {#each debugInfo.seenWords as word}
                                        <span class="bg-green-100 px-2 py-1 rounded">{word}</span>
                                    {/each}
                                </div>
                            </div>
                        </div>
                    </div>
                </Card>
            {/if}
        </div>
    </div>
</div>

<style>
    @keyframes wordAppear {
        0% {
            opacity: 0;
            transform: scale(0.5) translateY(-30px);
        }
        60% {
            transform: scale(1.1);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

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

    @keyframes float {
        0%,
        100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    .animate-word-appear {
        animation: wordAppear 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .animate-fade-in {
        animation: fadeIn 0.8s ease-out 0.3s both;
    }

    .word-display {
        animation: float 3s ease-in-out infinite;
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

    .animate-bounce-slow {
        animation: bounceSlow 3s ease-in-out infinite;
    }

    .animate-gradient {
        background-size: 200% 200%;
        animation: gradient 15s ease infinite;
    }
</style>
