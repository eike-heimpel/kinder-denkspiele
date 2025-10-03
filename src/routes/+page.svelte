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
     class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-8 animate-gradient"
 >
     <div class="max-w-5xl mx-auto">
         <div class="text-center mb-16 animate-fade-in">
             <div class="inline-block mb-6">
                 <span class="text-9xl animate-bounce-slow">🧠</span>
             </div>
             <h1
                 class="text-7xl font-black text-white mb-4 drop-shadow-2xl tracking-tight"
             >
                 Human Benchmark
             </h1>
             <p
                 class="text-3xl font-bold text-white/90 drop-shadow-lg tracking-wide"
             >
                 Deutsche Spiele für Kinder
             </p>
         </div>

        {#if loading}
            <Card>
                <p class="text-center text-xl">Lädt...</p>
            </Card>
         {:else if !selectedUser}
             <Card>
                 <div class="text-center mb-8">
                     <span class="text-6xl mb-4 inline-block">👥</span>
                     <h2 class="text-4xl font-black text-gray-800">
                         Wer spielt?
                     </h2>
                 </div>

                 {#if users.length > 0}
                     <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                         {#each users as user}
                             <button
                                 class="group relative bg-gradient-to-br from-blue-400 via-blue-500 to-purple-500 hover:from-blue-500 hover:via-purple-500 hover:to-pink-500 text-white text-3xl font-black py-10 px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-xl hover:shadow-2xl border-4 border-white/30"
                                 onclick={() => selectUser(user)}
                             >
                                 <span
                                     class="absolute top-2 right-2 text-4xl opacity-50 group-hover:opacity-100 transition-opacity"
                                     >🎮</span
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
                 <div class="text-center mb-10">
                     <h2 class="text-5xl font-black text-gray-800 mb-3">
                         Hallo, {selectedUser.name}! 👋
                     </h2>
                     <p class="text-2xl text-gray-600 font-semibold">
                         Wähle ein Spiel:
                     </p>
                 </div>

                 <div
                     class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-8 mb-8 border-4 border-purple-200 hover:border-purple-300 transition-all duration-300"
                 >
                     <div class="text-center mb-6">
                         <span class="text-6xl mb-4 inline-block">🗣️</span>
                         <h3 class="text-4xl font-black text-purple-700 mb-3">
                             Verbales Gedächtnis
                         </h3>
                         <p class="text-xl text-gray-700 font-medium">
                             Hast du dieses Wort schon einmal gesehen? Teste
                             dein Gedächtnis!
                         </p>
                     </div>

                     <div class="flex gap-6 justify-center flex-wrap">
                         <Button
                             variant="success"
                             size="lg"
                             onclick={() => startGame("easy")}
                         >
                             <div class="flex items-center gap-3">
                                 <span class="text-4xl">🟢</span>
                                 <span>Einfach</span>
                             </div>
                         </Button>
                         <Button
                             variant="danger"
                             size="lg"
                             onclick={() => startGame("hard")}
                         >
                             <div class="flex items-center gap-3">
                                 <span class="text-4xl">🔴</span>
                                 <span>Schwer</span>
                             </div>
                         </Button>
                     </div>
                 </div>

                 <div class="text-center">
                     <Button
                         variant="secondary"
                         size="md"
                         onclick={() => (selectedUser = null)}
                     >
                         ← Zurück
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
