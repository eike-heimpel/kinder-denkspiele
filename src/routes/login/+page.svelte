<script lang="ts">
    import Button from "$lib/components/Button.svelte";
    import Card from "$lib/components/Card.svelte";

    let password = $state("");
    let error = $state("");
    let loading = $state(false);

    async function handleLogin() {
        loading = true;
        error = "";

        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password }),
            });

            if (response.ok) {
                window.location.href = "/";
            } else {
                const data = await response.json();
                error = data.error || "Falsches Passwort";
            }
        } catch (e) {
            error = "Ein Fehler ist aufgetreten";
        } finally {
            loading = false;
        }
    }

    function handleKeyPress(event: KeyboardEvent) {
        if (event.key === "Enter") {
            handleLogin();
        }
    }
</script>

<div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-4"
>
    <div class="w-full max-w-md">
        <div class="text-center mb-8">
            <h1 class="text-5xl font-black text-white drop-shadow-2xl mb-2">
                🧠 Kinder Denkspiele
            </h1>
            <p class="text-white/90 text-lg font-bold">
                Bitte Passwort eingeben
            </p>
        </div>

        <Card>
            <div class="space-y-4">
                <div>
                    <label
                        for="password"
                        class="block text-sm font-bold text-gray-700 mb-2"
                    >
                        Passwort
                    </label>
                    <input
                        id="password"
                        type="password"
                        bind:value={password}
                        onkeypress={handleKeyPress}
                        class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-purple-500 transition-colors text-lg"
                        placeholder="Passwort eingeben..."
                        disabled={loading}
                    />
                </div>

                {#if error}
                    <div class="bg-red-50 border-2 border-red-200 rounded-xl p-3">
                        <p class="text-red-700 font-bold text-center">
                            ❌ {error}
                        </p>
                    </div>
                {/if}

                <Button
                    variant="primary"
                    size="lg"
                    onclick={handleLogin}
                    disabled={loading}
                    class="w-full"
                >
                    {loading ? "Wird überprüft..." : "Anmelden"}
                </Button>
            </div>
        </Card>
    </div>
</div>
