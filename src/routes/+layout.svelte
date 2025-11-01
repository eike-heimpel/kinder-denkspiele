<script>
	let { children } = $props();
	import "../app.css";
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";

	let isLoginPage = $derived($page.url.pathname === "/login");
	let isHomePage = $derived($page.url.pathname === "/");

	// Extract game title and emoji from path
	const gameInfo = $derived.by(() => {
		const path = $page.url.pathname;
		if (path.includes('/visual-memory')) return { emoji: '🎯', title: 'Visuelles Gedächtnis' };
		if (path.includes('/verbal-memory')) return { emoji: '🗣️', title: 'Verbales Gedächtnis' };
		if (path.includes('/reaction-time')) return { emoji: '⚡', title: 'Reaktionszeit' };
		if (path.includes('/logic-lab')) return { emoji: '🧩', title: 'Logik Labor' };
		return null;
	});

	async function handleLogout() {
		await fetch("/api/auth/logout", { method: "POST" });
		window.location.href = "/login";
	}

	function goHome() {
		goto("/");
	}
</script>

{#if !isLoginPage}
	<!-- Fixed navigation bar -->
	<div class="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-black/20 to-transparent backdrop-blur-sm px-2 py-2 flex items-center justify-between">
		{#if gameInfo}
			<div class="text-white font-bold text-lg drop-shadow-lg flex items-center gap-2">
				<span class="text-2xl">{gameInfo.emoji}</span>
				<span>{gameInfo.title}</span>
			</div>
		{:else}
			<div></div>
		{/if}

		<div class="flex gap-2">
			{#if !isHomePage}
				<button
					onclick={goHome}
					class="bg-white/80 hover:bg-white text-gray-700 px-3 py-1.5 rounded-lg shadow-lg transition-all duration-200 text-sm font-medium"
					title="Zur Startseite"
				>
					🏠 Start
				</button>
			{/if}
			<button
				onclick={handleLogout}
				class="bg-white/80 hover:bg-white text-gray-700 px-3 py-1.5 rounded-lg shadow-lg transition-all duration-200 text-sm font-medium"
				title="Abmelden"
			>
				Abmelden
			</button>
		</div>
	</div>

	<!-- Content wrapper with top padding to account for fixed navbar -->
	<div class="pt-14">
		{@render children()}
	</div>
{:else}
	<!-- No navbar on login page, render children directly -->
	{@render children()}
{/if}
