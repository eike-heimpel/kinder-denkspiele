<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import GameStats from "$lib/components/GameStats.svelte";

    let userId = $state("");
    let difficulty = $state<"easy" | "hard">("easy");
    let sessionId = $state<string | null>(null);
    let currentWord = $state<string | null>(null);
    let score = $state(0);
    let lives = $state(3);
    let gameOver = $state(false);
    let message = $state<string | null>(null);
    let loading = $state(true);
    let answering = $state(false);

    onMount(() => {
        const params = new URLSearchParams(window.location.search);
        userId = params.get("userId") || "";
        difficulty = (params.get("difficulty") as "easy" | "hard") || "easy";

        if (!userId) {
            goto("/");
            return;
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
            gameOver = false;
            message = null;
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

            if (data.gameOver) {
                gameOver = true;
                message = data.message;
                currentWord = null;
            } else {
                currentWord = data.currentWord;
                score = data.score;
                lives = data.lives;
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

<svelte:window onkeydown={handleKeyPress} />

<svelte:head>
    <title>Verbales Gedächtnis - Human Benchmark</title>
</svelte:head>

<div
    class="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-8"
>
    <div class="max-w-4xl mx-auto">
        <h1
            class="text-5xl font-bold text-white text-center mb-8 drop-shadow-lg"
        >
            🗣️ Verbales Gedächtnis
        </h1>

        <Card class="mb-6">
            <GameStats {score} {lives} />
        </Card>

        {#if loading}
            <Card>
                <div class="text-center py-20">
                    <p class="text-3xl font-bold text-gray-700">
                        Spiel wird geladen...
                    </p>
                </div>
            </Card>
        {:else if gameOver}
            <Card>
                <div class="text-center py-12">
                    <p class="text-5xl mb-6">🎮</p>
                    <p class="text-4xl font-bold text-gray-800 mb-4">
                        {message}
                    </p>
                    <p class="text-2xl text-gray-600 mb-8">
                        Schwierigkeit: {difficulty === "easy"
                            ? "🟢 Einfach"
                            : "🔴 Schwer"}
                    </p>
                    <div class="flex gap-4 justify-center">
                        <Button variant="success" size="lg" onclick={startGame}>
                            🔄 Nochmal spielen
                        </Button>
                        <Button
                            variant="secondary"
                            size="lg"
                            onclick={() => goto("/")}
                        >
                            🏠 Zur Startseite
                        </Button>
                    </div>
                </div>
            </Card>
        {:else if currentWord}
            <Card>
                <div class="text-center py-16">
                    <p
                        class="text-7xl font-bold text-gray-800 mb-12 animate-pulse"
                    >
                        {currentWord}
                    </p>

                    <p class="text-2xl text-gray-600 mb-8">
                        Hast du dieses Wort schon gesehen?
                    </p>

                    <div class="flex gap-6 justify-center">
                        <Button
                            variant="danger"
                            size="xl"
                            onclick={() => submitAnswer("new")}
                            disabled={answering}
                        >
                            NEU<br />
                            <span class="text-sm">(← oder N)</span>
                        </Button>
                        <Button
                            variant="success"
                            size="xl"
                            onclick={() => submitAnswer("seen")}
                            disabled={answering}
                        >
                            GESEHEN<br />
                            <span class="text-sm">(→ oder G)</span>
                        </Button>
                    </div>
                </div>
            </Card>
        {/if}

        <div class="text-center mt-6">
            <Button variant="secondary" onclick={() => goto("/")}>
                ← Zurück zur Startseite
            </Button>
        </div>
    </div>
</div>

<style>
    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.9;
            transform: scale(1.05);
        }
    }

    .animate-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
</style>
