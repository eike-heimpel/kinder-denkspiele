<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';

	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit() {
		if (!password) {
			error = 'Bitte geben Sie das Passwort ein';
			return;
		}

		loading = true;
		error = '';

		try {
			const response = await fetch('/api/admin/verify', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ password })
			});

			const data = await response.json();

			if (data.success) {
				goto('/admin');
			} else {
				error = data.error || 'Falsches Passwort';
				password = '';
			}
		} catch (err) {
			error = 'Ein Fehler ist aufgetreten';
		} finally {
			loading = false;
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleSubmit();
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-500 via-gray-500 to-zinc-500 p-4 flex items-center justify-center">
	<div class="max-w-md w-full">
		<div class="text-center mb-8">
			<h1 class="text-5xl font-black text-white drop-shadow-2xl mb-2">🔐 Admin</h1>
			<p class="text-white/90 text-lg font-bold">Passwort eingeben</p>
		</div>

		<Card>
			<div class="space-y-4">
				<div>
					<label for="password" class="block text-sm font-bold text-gray-700 mb-2">
						Passwort
					</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						onkeypress={handleKeyPress}
						placeholder="Passwort eingeben..."
						class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl
                               focus:outline-none focus:border-slate-500 transition-colors
                               text-lg"
						disabled={loading}
					/>
				</div>

				{#if error}
					<div class="bg-red-50 border-2 border-red-200 rounded-xl p-3">
						<p class="text-red-700 font-bold text-center">❌ {error}</p>
					</div>
				{/if}

				<Button
					variant="primary"
					size="lg"
					onclick={handleSubmit}
					disabled={loading}
					class="w-full"
				>
					{loading ? 'Überprüfe...' : 'Anmelden'}
				</Button>

				<Button
					variant="secondary"
					size="md"
					onclick={() => goto('/')}
					disabled={loading}
					class="w-full"
				>
					← Zurück
				</Button>
			</div>
		</Card>
	</div>
</div>
