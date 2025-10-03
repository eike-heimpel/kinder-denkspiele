<script lang="ts">
    interface Props {
        score: number;
        lives: number;
        round: number;
    }

    let { score, lives, round }: Props = $props();
</script>

<div
    class="flex justify-between items-center gap-8 text-2xl font-extrabold bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 border-2 border-purple-200"
>
    <div class="flex items-center gap-3">
        <span class="text-blue-700 text-3xl">🎯</span>
        <div class="flex flex-col">
            <span class="text-sm text-blue-600 uppercase tracking-wider"
                >Runde</span
            >
            <span
                class="text-4xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent font-black"
                >{round}</span
            >
        </div>
    </div>

    <div class="flex items-center gap-3">
        <span class="text-purple-700 text-3xl">🏆</span>
        <div class="flex flex-col">
            <span class="text-sm text-purple-600 uppercase tracking-wider"
                >Punkte</span
            >
            <span
                class="text-4xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent"
                >{score}</span
            >
        </div>
    </div>

    <div class="flex items-center gap-3">
        <span class="text-sm text-purple-600 uppercase tracking-wider"
            >Leben</span
        >
        <div class="flex gap-2">
            {#each Array(3) as _, i}
                <span class="text-4xl transition-all duration-300 {i < lives ? 'scale-110 drop-shadow-lg' : 'scale-90 grayscale'}">
                    {i < lives ? "❤️" : "🖤"}
                </span>
            {/each}
        </div>
    </div>
</div>
