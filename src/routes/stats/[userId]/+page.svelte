<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import type { GameStats } from "$lib/types";

    let userId = $state("");
    let userName = $state("");
    let verbalEasyStats = $state<GameStats | null>(null);
    let verbalHardStats = $state<GameStats | null>(null);
    let visualEasyStats = $state<GameStats | null>(null);
    let visualHardStats = $state<GameStats | null>(null);
    let loading = $state(true);

    onMount(async () => {
        userId = $page.params.userId || "";
        if (!userId) {
            goto("/");
            return;
        }
        await loadStats();
    });

    async function loadStats() {
        loading = true;

        const userResponse = await fetch(`/api/users/${userId}`);
        if (userResponse.ok) {
            const user = await userResponse.json();
            userName = user.name;
        }

        const [verbalEasy, verbalHard, visualEasy, visualHard] =
            await Promise.all([
                fetch(
                    `/api/game/verbal-memory/stats?userId=${userId}&difficulty=easy`,
                ),
                fetch(
                    `/api/game/verbal-memory/stats?userId=${userId}&difficulty=hard`,
                ),
                fetch(
                    `/api/game/visual-memory/stats?userId=${userId}&difficulty=easy`,
                ),
                fetch(
                    `/api/game/visual-memory/stats?userId=${userId}&difficulty=hard`,
                ),
            ]);

        if (verbalEasy.ok) verbalEasyStats = await verbalEasy.json();
        if (verbalHard.ok) verbalHardStats = await verbalHard.json();
        if (visualEasy.ok) visualEasyStats = await visualEasy.json();
        if (visualHard.ok) visualHardStats = await visualHard.json();

        loading = false;
    }

    function formatDate(date?: Date) {
        if (!date) return "Nie gespielt";
        return new Date(date).toLocaleDateString("de-DE", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
        });
    }
</script>

<svelte:head>
    <title>Statistiken - {userName}</title>
</svelte:head>

<div
    class="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-4 animate-gradient"
>
    <div class="max-w-4xl mx-auto">
        <div class="text-center mb-4">
            <h1 class="text-3xl font-black text-white drop-shadow-2xl">
                Statistiken
            </h1>
            {#if userName}
                <p class="text-xl font-bold text-white/90 mt-1">
                    {userName}
                </p>
            {/if}
        </div>

        {#if loading}
            <Card>
                <p class="text-center text-lg py-8">Lädt Statistiken...</p>
            </Card>
        {:else}
            <div class="space-y-4">
                <!-- Verbal Memory Stats -->
                <Card>
                    <h2 class="text-2xl font-black text-gray-800 mb-4">
                        Verbales Gedächtnis
                    </h2>

                    <div class="grid md:grid-cols-2 gap-4">
                        <!-- Easy Stats -->
                        <div
                            class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border-2 border-green-200"
                        >
                            <div
                                class="text-sm font-bold text-green-700 uppercase tracking-wider mb-3"
                            >
                                Einfach
                            </div>

                            {#if verbalEasyStats && verbalEasyStats.totalGames > 0}
                                <div class="space-y-2">
                                    <div class="flex justify-between items-end">
                                        <span class="text-sm text-gray-600"
                                            >Höchste Punktzahl</span
                                        >
                                        <span
                                            class="text-3xl font-black text-green-700"
                                            >{verbalEasyStats.highScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Durchschnitt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{verbalEasyStats.averageScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Spiele gespielt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{verbalEasyStats.totalGames}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Zuletzt gespielt</span
                                        >
                                        <span
                                            class="text-sm font-medium text-gray-600"
                                            >{formatDate(
                                                verbalEasyStats.lastPlayed,
                                            )}</span
                                        >
                                    </div>
                                </div>
                            {:else}
                                <p class="text-gray-500 text-center py-4">
                                    Noch keine Spiele
                                </p>
                            {/if}
                        </div>

                        <!-- Hard Stats -->
                        <div
                            class="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl p-4 border-2 border-red-200"
                        >
                            <div
                                class="text-sm font-bold text-red-700 uppercase tracking-wider mb-3"
                            >
                                Schwer
                            </div>

                            {#if verbalHardStats && verbalHardStats.totalGames > 0}
                                <div class="space-y-2">
                                    <div class="flex justify-between items-end">
                                        <span class="text-sm text-gray-600"
                                            >Höchste Punktzahl</span
                                        >
                                        <span
                                            class="text-3xl font-black text-red-700"
                                            >{verbalHardStats.highScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Durchschnitt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{verbalHardStats.averageScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Spiele gespielt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{verbalHardStats.totalGames}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Zuletzt gespielt</span
                                        >
                                        <span
                                            class="text-sm font-medium text-gray-600"
                                            >{formatDate(
                                                verbalHardStats.lastPlayed,
                                            )}</span
                                        >
                                    </div>
                                </div>
                            {:else}
                                <p class="text-gray-500 text-center py-4">
                                    Noch keine Spiele
                                </p>
                            {/if}
                        </div>
                    </div>
                </Card>

                <!-- Visual Memory Stats -->
                <Card>
                    <h2 class="text-2xl font-black text-gray-800 mb-4">
                        Visuelles Gedächtnis
                    </h2>

                    <div class="grid md:grid-cols-2 gap-4">
                        <!-- Easy Stats -->
                        <div
                            class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border-2 border-green-200"
                        >
                            <div
                                class="text-sm font-bold text-green-700 uppercase tracking-wider mb-3"
                            >
                                Einfach
                            </div>

                            {#if visualEasyStats && visualEasyStats.totalGames > 0}
                                <div class="space-y-2">
                                    <div class="flex justify-between items-end">
                                        <span class="text-sm text-gray-600"
                                            >Höchste Punktzahl</span
                                        >
                                        <span
                                            class="text-3xl font-black text-green-700"
                                            >{visualEasyStats.highScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Durchschnitt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{visualEasyStats.averageScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Spiele gespielt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{visualEasyStats.totalGames}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Zuletzt gespielt</span
                                        >
                                        <span
                                            class="text-sm font-medium text-gray-600"
                                            >{formatDate(
                                                visualEasyStats.lastPlayed,
                                            )}</span
                                        >
                                    </div>
                                </div>
                            {:else}
                                <p class="text-gray-500 text-center py-4">
                                    Noch keine Spiele
                                </p>
                            {/if}
                        </div>

                        <!-- Hard Stats -->
                        <div
                            class="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl p-4 border-2 border-red-200"
                        >
                            <div
                                class="text-sm font-bold text-red-700 uppercase tracking-wider mb-3"
                            >
                                Schwer
                            </div>

                            {#if visualHardStats && visualHardStats.totalGames > 0}
                                <div class="space-y-2">
                                    <div class="flex justify-between items-end">
                                        <span class="text-sm text-gray-600"
                                            >Höchste Punktzahl</span
                                        >
                                        <span
                                            class="text-3xl font-black text-red-700"
                                            >{visualHardStats.highScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Durchschnitt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{visualHardStats.averageScore}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Spiele gespielt</span
                                        >
                                        <span
                                            class="text-lg font-bold text-gray-700"
                                            >{visualHardStats.totalGames}</span
                                        >
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-600"
                                            >Zuletzt gespielt</span
                                        >
                                        <span
                                            class="text-sm font-medium text-gray-600"
                                            >{formatDate(
                                                visualHardStats.lastPlayed,
                                            )}</span
                                        >
                                    </div>
                                </div>
                            {:else}
                                <p class="text-gray-500 text-center py-4">
                                    Noch keine Spiele
                                </p>
                            {/if}
                        </div>
                    </div>
                </Card>
            </div>

            <div class="text-center mt-4">
                <Button variant="secondary" onclick={() => goto("/")}>
                    ← Zurück zur Startseite
                </Button>
            </div>
        {/if}
    </div>
</div>

<style>
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

    .animate-gradient {
        background-size: 200% 200%;
        animation: gradient 15s ease infinite;
    }
</style>
