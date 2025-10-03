<script lang="ts">
    interface Props {
        score: number;
        lives: number;
    }

    let { score, lives }: Props = $props();
</script>

<div class="flex justify-between items-center gap-8 text-2xl font-bold">
    <div class="flex items-center gap-2">
        <span class="text-gray-600">Punkte:</span>
        <span class="text-blue-600">{score}</span>
    </div>

    <div class="flex items-center gap-2">
        <span class="text-gray-600">Leben:</span>
        <div class="flex gap-1">
            {#each Array(3) as _, i}
                <span class="text-3xl">
                    {i < lives ? "❤️" : "🖤"}
                </span>
            {/each}
        </div>
    </div>
</div>
