<script lang="ts">
    interface Props {
        score: number;
        lives: number;
        round: number;
    }

    let { score, lives, round }: Props = $props();
</script>

<div
    class="flex justify-between items-center gap-4 text-xl font-extrabold bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-4 border-2 border-purple-200"
>
    <div class="flex items-center gap-2">
        <span class="text-blue-700 text-2xl">🎯</span>
        <div class="flex flex-col">
            <span class="text-xs text-blue-600 uppercase tracking-wider"
                >Runde</span
            >
            <span
                class="text-3xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent font-black"
                >{round}</span
            >
        </div>
    </div>

    <div class="flex items-center gap-2">
        <span class="text-purple-700 text-2xl">🏆</span>
        <div class="flex flex-col">
            <span class="text-xs text-purple-600 uppercase tracking-wider"
                >Punkte</span
            >
            <span
                class="text-3xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent"
                >{score}</span
            >
        </div>
    </div>

    <div class="flex items-center gap-2">
        <span class="text-xs text-purple-600 uppercase tracking-wider"
            >Leben</span
        >
        <div class="flex gap-1">
            {#each Array(3) as _, i}
                <span
                    class="text-3xl transition-all duration-300 {i < lives
                        ? 'scale-110 drop-shadow-lg'
                        : 'scale-90 grayscale'}"
                >
                    {i < lives ? "❤️" : "🖤"}
                </span>
            {/each}
        </div>
    </div>
</div>
