<script>
	let { children } = $props();
	import "../app.css";
	import { page } from "$app/stores";

	let isLoginPage = $derived($page.url.pathname === "/login");

	async function handleLogout() {
		await fetch("/api/auth/logout", { method: "POST" });
		window.location.href = "/login";
	}
</script>

{#if !isLoginPage}
	<button
		onclick={handleLogout}
		class="fixed top-4 right-4 z-50 bg-white/80 hover:bg-white text-gray-700 px-4 py-2 rounded-xl shadow-lg transition-all duration-200 text-sm font-medium"
	>
		Abmelden
	</button>
{/if}

{@render children()}
