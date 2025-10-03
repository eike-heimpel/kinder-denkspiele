<script lang="ts">
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import type { User } from "$lib/types";

    let users = $state<User[]>([]);
    let newUserName = $state("");
    let loading = $state(true);
    let selectedUser = $state<User | null>(null);
    let showNewUserForm = $state(false);

    onMount(async () => {
        await loadUsers();
        loading = false;
    });

    async function loadUsers() {
        const response = await fetch("/api/users");
        users = await response.json();
    }

    async function createUser() {
        if (!newUserName.trim()) return;

        const response = await fetch("/api/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newUserName.trim() }),
        });

        if (response.ok) {
            await loadUsers();
            newUserName = "";
            showNewUserForm = false;
        }
    }

    function selectUser(user: User) {
        selectedUser = user;
    }

    function startGame(difficulty: "easy" | "hard") {
        if (!selectedUser) return;
        goto(
            `/game/verbal-memory?userId=${selectedUser._id}&difficulty=${difficulty}`,
        );
    }
</script>

<svelte:head>
    <title>Human Benchmark - Deutsche Spiele für Kinder</title>
</svelte:head>

<div
    class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-8"
>
    <div class="max-w-4xl mx-auto">
        <h1
            class="text-6xl font-bold text-white text-center mb-4 drop-shadow-lg"
        >
            🧠 Human Benchmark
        </h1>
        <p class="text-2xl text-white text-center mb-12 drop-shadow">
            Deutsche Spiele für Kinder
        </p>

        {#if loading}
            <Card>
                <p class="text-center text-xl">Lädt...</p>
            </Card>
        {:else if !selectedUser}
            <Card>
                <h2 class="text-3xl font-bold mb-6 text-gray-800">
                    Wer spielt?
                </h2>

                {#if users.length > 0}
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        {#each users as user}
                            <button
                                class="bg-gradient-to-r from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600 text-white text-2xl font-bold py-8 px-6 rounded-xl transition-all transform hover:scale-105 active:scale-95"
                                onclick={() => selectUser(user)}
                            >
                                {user.name}
                            </button>
                        {/each}
                    </div>
                {/if}

                {#if !showNewUserForm}
                    <Button
                        variant="success"
                        size="lg"
                        onclick={() => (showNewUserForm = true)}
                    >
                        ➕ Neuer Spieler
                    </Button>
                {:else}
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <input
                            type="text"
                            bind:value={newUserName}
                            placeholder="Dein Name"
                            class="w-full px-4 py-3 text-xl border-2 border-gray-300 rounded-lg mb-4"
                            onkeydown={(e) => e.key === "Enter" && createUser()}
                        />
                        <div class="flex gap-4">
                            <Button variant="success" onclick={createUser}>
                                Erstellen
                            </Button>
                            <Button
                                variant="secondary"
                                onclick={() => (showNewUserForm = false)}
                            >
                                Abbrechen
                            </Button>
                        </div>
                    </div>
                {/if}
            </Card>
        {:else}
            <Card>
                <h2 class="text-3xl font-bold mb-2 text-gray-800">
                    Hallo, {selectedUser.name}! 👋
                </h2>
                <p class="text-xl text-gray-600 mb-8">Wähle ein Spiel:</p>

                <div class="mb-8">
                    <h3 class="text-2xl font-bold mb-4 text-purple-600">
                        🗣️ Verbales Gedächtnis
                    </h3>
                    <p class="text-gray-700 mb-6">
                        Hast du dieses Wort schon einmal gesehen? Teste dein
                        Gedächtnis!
                    </p>

                    <div class="flex gap-4">
                        <Button
                            variant="success"
                            size="lg"
                            onclick={() => startGame("easy")}
                        >
                            🟢 Einfach
                        </Button>
                        <Button
                            variant="danger"
                            size="lg"
                            onclick={() => startGame("hard")}
                        >
                            🔴 Schwer
                        </Button>
                    </div>
                </div>

                <Button
                    variant="secondary"
                    onclick={() => (selectedUser = null)}
                >
                    ← Zurück
                </Button>
            </Card>
        {/if}
    </div>
</div>
