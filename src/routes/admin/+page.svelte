<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';
	import type { User } from '$lib/types';

	let users = $state<User[]>([]);
	let loading = $state(true);
	let error = $state('');
	let deletingUserId = $state<string | null>(null);

	onMount(async () => {
		await loadUsers();
	});

	async function loadUsers() {
		loading = true;
		error = '';

		try {
			const response = await fetch('/api/users');
			if (!response.ok) throw new Error('Fehler beim Laden der Benutzer');
			users = await response.json();
		} catch (err) {
			error = 'Fehler beim Laden der Benutzer';
			console.error(err);
		} finally {
			loading = false;
		}
	}

	async function deleteUser(userId: string | undefined, userName: string) {
		if (!userId) return;

		const confirmed = confirm(
			`Möchten Sie "${userName}" wirklich löschen?\n\nDies kann nicht rückgängig gemacht werden.`
		);

		if (!confirmed) return;

		deletingUserId = userId;
		error = '';

		try {
			const response = await fetch(`/api/users/${userId}`, {
				method: 'DELETE'
			});

			if (!response.ok) throw new Error('Fehler beim Löschen');

			await loadUsers();
		} catch (err) {
			error = `Fehler beim Löschen von ${userName}`;
			console.error(err);
		} finally {
			deletingUserId = null;
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-500 via-gray-500 to-zinc-500 p-4">
	<div class="max-w-4xl mx-auto">
		<div class="text-center mb-6">
			<h1 class="text-5xl font-black text-white drop-shadow-2xl mb-2">🔧 Admin Panel</h1>
			<p class="text-white/90 text-lg font-bold">Benutzerverwaltung</p>
		</div>

		<div class="mb-4">
			<Button variant="secondary" size="md" onclick={() => goto('/')}>
				← Zurück zur Startseite
			</Button>
		</div>

		<Card>
			<h2 class="text-3xl font-black text-gray-800 mb-6">Alle Benutzer</h2>

			{#if error}
				<div class="bg-red-50 border-2 border-red-200 rounded-xl p-4 mb-4">
					<p class="text-red-700 font-bold text-center">❌ {error}</p>
				</div>
			{/if}

			{#if loading}
				<div class="text-center py-12">
					<p class="text-2xl font-bold text-gray-500">Lädt...</p>
				</div>
			{:else if users.length === 0}
				<div class="text-center py-12">
					<p class="text-2xl font-bold text-gray-500">Keine Benutzer gefunden</p>
				</div>
			{:else}
				<div class="space-y-3">
					{#each users as user (user._id)}
						<div
							class="flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-gray-50
                                   border-2 border-slate-200 rounded-xl hover:shadow-md transition-all"
						>
							<div class="flex items-center gap-4">
								<span class="text-5xl">{user.avatar}</span>
								<div>
									<p class="text-xl font-black text-gray-800">{user.name}</p>
									<p class="text-sm text-gray-500">ID: {user._id}</p>
								</div>
							</div>

							<Button
								variant="danger"
								size="md"
								onclick={() => deleteUser(user._id, user.name)}
								disabled={deletingUserId === user._id}
							>
								{deletingUserId === user._id ? 'Löscht...' : '🗑️ Löschen'}
							</Button>
						</div>
					{/each}
				</div>

				<div class="mt-6 pt-6 border-t-2 border-gray-200">
					<div class="flex items-center justify-between text-sm text-gray-600">
						<p class="font-bold">Gesamt: {users.length} Benutzer</p>
						<Button variant="secondary" size="sm" onclick={loadUsers}>
							🔄 Aktualisieren
						</Button>
					</div>
				</div>
			{/if}
		</Card>
	</div>
</div>
