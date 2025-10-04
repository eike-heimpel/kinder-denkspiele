<script lang="ts">
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
</script>

<div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-4"
>
    <div class="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-800 mb-2">
                🧠 Kinder Denkspiele
            </h1>
            <p class="text-gray-600">Bitte Passwort eingeben</p>
        </div>

        <form
            onsubmit={(e) => {
                e.preventDefault();
                handleLogin();
            }}
        >
            <div class="mb-6">
                <label
                    for="password"
                    class="block text-sm font-medium text-gray-700 mb-2"
                >
                    Passwort
                </label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-purple-500 transition-colors"
                    placeholder="Passwort eingeben..."
                    disabled={loading}
                    required
                />
            </div>

            {#if error}
                <div
                    class="mb-4 p-3 bg-red-100 border-2 border-red-300 rounded-xl text-red-700 text-sm"
                >
                    {error}
                </div>
            {/if}

            <button
                type="submit"
                disabled={loading}
                class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold py-3 px-6 rounded-xl hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
                {loading ? "Wird überprüft..." : "Anmelden"}
            </button>
        </form>
    </div>
</div>
