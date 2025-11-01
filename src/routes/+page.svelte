<script lang="ts">
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";
    import type { User } from "$lib/types";

    let users = $state<User[]>([]);
    let newUserName = $state("");
    let newUserAvatar = $state("😀");
    let loading = $state(true);
    let selectedUser = $state<User | null>(null);
    let showNewUserForm = $state(false);

    const avatarOptions = [
        "😀", "😃", "😄", "😁", "😊", "🙂", "😇", "🥰", "😍", "🤩",
        "😎", "🤓", "🧐", "🤔", "🤗", "🤠", "👦", "👧", "🧒", "👶",
        "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
        "🦁", "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🦄", "🐙", "🦋",
        "🌟", "⭐", "🌈", "🔥", "💎", "👑", "🎈", "🎨", "⚽", "🎮"
    ];

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
            body: JSON.stringify({
                name: newUserName.trim(),
                avatar: newUserAvatar
            }),
        });

        if (response.ok) {
            await loadUsers();
            newUserName = "";
            newUserAvatar = "😀";
            showNewUserForm = false;
        }
    }

    function selectUser(user: User) {
        selectedUser = user;
    }

    function startGame(
        gameType: "verbal-memory" | "visual-memory" | "reaction-time" | "logic-lab",
        difficulty: "easy" | "hard",
    ) {
        if (!selectedUser) return;
        goto(
            `/game/${gameType}?userId=${selectedUser._id}&difficulty=${difficulty}`,
        );
    }
</script>

<svelte:head>
    <title
        >Kinder Denkspiele - Spielerisch lernen und Gedächtnis trainieren</title
    >
</svelte:head>

<div
    class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-4 animate-gradient"
>
    <div class="max-w-4xl mx-auto pt-4">
        <div class="text-center mb-4 animate-fade-in">
            <div class="inline-block mb-1">
                <span class="text-5xl animate-bounce-slow">🧠</span>
            </div>
            <h1
                class="text-3xl font-black text-white mb-1 drop-shadow-2xl tracking-tight"
            >
                Kinder Denkspiele
            </h1>
            <p class="text-lg font-bold text-white/90 drop-shadow-lg">
                Spielerisch lernen und trainieren
            </p>
        </div>

        {#if loading}
            <Card>
                <p class="text-center text-xl">Lädt...</p>
            </Card>
        {:else if !selectedUser}
            <Card>
                <div class="text-center mb-4">
                    <span class="text-4xl mb-2 inline-block">👥</span>
                    <h2 class="text-3xl font-black text-gray-800">
                        Wer spielt?
                    </h2>
                </div>

                {#if users.length > 0}
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        {#each users as user}
                            <button
                                class="group relative bg-gradient-to-br from-blue-400 via-blue-500 to-purple-500 hover:from-blue-500 hover:via-purple-500 hover:to-pink-500 text-white text-2xl font-black py-6 px-6 rounded-2xl transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-xl hover:shadow-2xl border-4 border-white/30"
                                onclick={() => selectUser(user)}
                            >
                                <div class="flex items-center justify-center gap-3">
                                    <span class="text-5xl">{user.avatar}</span>
                                    <span>{user.name}</span>
                                </div>
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
                    <div class="bg-gray-50 p-4 rounded-xl">
                        <div class="mb-3 text-center">
                            <p class="text-sm font-bold text-gray-700 mb-2">Wähle dein Avatar:</p>
                            <div class="text-6xl mb-2">{newUserAvatar}</div>
                            <div class="grid grid-cols-10 gap-2 max-h-48 overflow-y-auto p-2 bg-white rounded-lg border-2 border-gray-200">
                                {#each avatarOptions as avatar}
                                    <button
                                        type="button"
                                        class="text-3xl hover:scale-125 transition-transform duration-200 cursor-pointer p-1 rounded {newUserAvatar === avatar ? 'bg-blue-200 scale-110' : ''}"
                                        onclick={() => newUserAvatar = avatar}
                                    >
                                        {avatar}
                                    </button>
                                {/each}
                            </div>
                        </div>
                        <input
                            type="text"
                            bind:value={newUserName}
                            placeholder="Dein Name"
                            class="w-full px-3 py-2 text-lg border-2 border-gray-300 rounded-lg mb-3"
                            onkeydown={(e) => e.key === "Enter" && createUser()}
                        />
                        <div class="flex gap-3">
                            <Button variant="success" onclick={createUser}>
                                Erstellen
                            </Button>
                            <Button
                                variant="secondary"
                                onclick={() => {
                                    showNewUserForm = false;
                                    newUserName = "";
                                    newUserAvatar = "😀";
                                }}
                            >
                                Abbrechen
                            </Button>
                        </div>
                    </div>
                {/if}
            </Card>
        {:else}
            <Card>
                <div class="text-center mb-4">
                    <h2 class="text-3xl font-black text-gray-800 mb-2">
                        Hallo, {selectedUser.name}! 👋
                    </h2>
                    <p class="text-xl text-gray-600 font-semibold">
                        Wähle ein Spiel:
                    </p>
                </div>

                <div
                    class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-5 mb-4 border-4 border-purple-200 hover:border-purple-300 transition-all duration-300"
                >
                    <div class="text-center mb-4">
                        <span class="text-4xl mb-2 inline-block">🗣️</span>
                        <h3 class="text-2xl font-black text-purple-700 mb-2">
                            Verbales Gedächtnis
                        </h3>
                        <p class="text-base text-gray-700 font-medium">
                            Hast du dieses Wort schon einmal gesehen? Teste dein
                            Gedächtnis!
                        </p>
                    </div>

                    <div class="flex gap-4 justify-center flex-wrap">
                        <Button
                            variant="success"
                            size="lg"
                            onclick={() => startGame("verbal-memory", "easy")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🟢</span>
                                <span>Einfach</span>
                            </div>
                        </Button>
                        <Button
                            variant="danger"
                            size="lg"
                            onclick={() => startGame("verbal-memory", "hard")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🔴</span>
                                <span>Schwer</span>
                            </div>
                        </Button>
                    </div>
                </div>

                <div
                    class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl p-5 mb-4 border-4 border-blue-200 hover:border-blue-300 transition-all duration-300"
                >
                    <div class="text-center mb-4">
                        <span class="text-4xl mb-2 inline-block">🎯</span>
                        <h3 class="text-2xl font-black text-blue-700 mb-2">
                            Visuelles Gedächtnis
                        </h3>
                        <p class="text-base text-gray-700 font-medium">
                            Merke dir die Position der blauen Quadrate und finde
                            sie wieder!
                        </p>
                    </div>

                    <div class="flex gap-4 justify-center flex-wrap">
                        <Button
                            variant="success"
                            size="lg"
                            onclick={() => startGame("visual-memory", "easy")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🟢</span>
                                <span>Einfach</span>
                            </div>
                        </Button>
                        <Button
                            variant="danger"
                            size="lg"
                            onclick={() => startGame("visual-memory", "hard")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🔴</span>
                                <span>Schwer</span>
                            </div>
                        </Button>
                    </div>
                </div>

                <div
                    class="bg-gradient-to-br from-orange-50 to-red-50 rounded-3xl p-5 mb-4 border-4 border-orange-200 hover:border-orange-300 transition-all duration-300"
                >
                    <div class="text-center mb-4">
                        <span class="text-4xl mb-2 inline-block">⚡</span>
                        <h3 class="text-2xl font-black text-orange-700 mb-2">
                            Reaktionszeit
                        </h3>
                        <p class="text-base text-gray-700 font-medium">
                            Wie schnell kannst du reagieren? Teste deine
                            Reaktionsgeschwindigkeit!
                        </p>
                    </div>

                    <div class="flex gap-4 justify-center flex-wrap">
                        <Button
                            variant="success"
                            size="lg"
                            onclick={() => startGame("reaction-time", "easy")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🟢</span>
                                <span>Einfach</span>
                            </div>
                        </Button>
                        <Button
                            variant="danger"
                            size="lg"
                            onclick={() => startGame("reaction-time", "hard")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🔴</span>
                                <span>Schwer</span>
                            </div>
                        </Button>
                    </div>
                </div>

                <div
                    class="bg-gradient-to-br from-green-50 to-teal-50 rounded-3xl p-5 mb-4 border-4 border-green-200 hover:border-green-300 transition-all duration-300"
                >
                    <div class="text-center mb-4">
                        <span class="text-4xl mb-2 inline-block">🧠</span>
                        <h3 class="text-2xl font-black text-green-700 mb-2">
                            Logik-Labor
                        </h3>
                        <p class="text-base text-gray-700 font-medium">
                            Löse spannende Rätsel! KI erstellt neue Aufgaben für
                            dich.
                        </p>
                    </div>

                    <div class="flex gap-4 justify-center flex-wrap">
                        <Button
                            variant="success"
                            size="lg"
                            onclick={() => startGame("logic-lab", "easy")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🟢</span>
                                <span>Einfach</span>
                            </div>
                        </Button>
                        <Button
                            variant="danger"
                            size="lg"
                            onclick={() => startGame("logic-lab", "hard")}
                        >
                            <div class="flex items-center gap-2">
                                <span class="text-3xl">🔴</span>
                                <span>Schwer</span>
                            </div>
                        </Button>
                    </div>
                </div>

                <div class="flex gap-3 justify-center flex-wrap">
                    <Button
                        variant="secondary"
                        size="md"
                        onclick={() => (selectedUser = null)}
                    >
                        ← Zurück
                    </Button>
                    <Button
                        variant="primary"
                        size="md"
                        onclick={() =>
                            selectedUser && goto(`/stats/${selectedUser._id}`)}
                    >
                        Statistiken ansehen
                    </Button>
                </div>
            </Card>
        {/if}
    </div>
</div>

<style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
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
</style>
