<script lang="ts">
    type GridMode = "showing" | "memorizing" | "recalling" | "feedback";

    interface Props {
        gridSize: number;
        targetPositions: number[];
        userSelections: number[];
        mode: GridMode;
        onSquareClick?: (index: number) => void;
        disabled?: boolean;
    }

    let {
        gridSize,
        targetPositions,
        userSelections,
        mode,
        onSquareClick,
        disabled = false,
    }: Props = $props();

    const totalSquares = $derived(gridSize * gridSize);
    const squares = $derived(Array.from({ length: totalSquares }, (_, i) => i));

    function isTarget(index: number): boolean {
        return targetPositions.includes(index);
    }

    function isSelected(index: number): boolean {
        return userSelections.includes(index);
    }

    function getSquareState(
        index: number,
    ): "correct" | "incorrect" | "missed" | "neutral" {
        if (mode !== "feedback") return "neutral";

        const wasTarget = isTarget(index);
        const wasSelected = isSelected(index);

        if (wasTarget && wasSelected) return "correct";
        if (!wasTarget && wasSelected) return "incorrect";
        if (wasTarget && !wasSelected) return "missed";
        return "neutral";
    }

    function handleSquareClick(index: number) {
        if (disabled || mode !== "recalling") return;
        onSquareClick?.(index);
    }
</script>

<div
    class="grid gap-3 mx-auto"
    style="grid-template-columns: repeat({gridSize}, minmax(0, 1fr)); max-width: {gridSize *
        100}px;"
>
    {#each squares as index}
        <button
            type="button"
            class="grid-square aspect-square rounded-2xl transition-all duration-300 border-4
                {mode === 'showing' && isTarget(index)
                ? 'bg-blue-500 border-blue-600 shadow-2xl scale-105'
                : ''}
                {mode === 'recalling' && isSelected(index)
                ? 'bg-purple-400 border-purple-500'
                : ''}
                {mode === 'recalling' && !isSelected(index)
                ? 'bg-white border-gray-300 hover:border-gray-400 hover:shadow-lg'
                : ''}
                {mode === 'memorizing' ? 'bg-white border-gray-300' : ''}
                {mode === 'feedback' && getSquareState(index) === 'correct'
                ? 'bg-green-500 border-green-600'
                : ''}
                {mode === 'feedback' && getSquareState(index) === 'incorrect'
                ? 'bg-red-500 border-red-600'
                : ''}
                {mode === 'feedback' && getSquareState(index) === 'missed'
                ? 'bg-orange-400 border-orange-500'
                : ''}
                {mode === 'feedback' && getSquareState(index) === 'neutral'
                ? 'bg-white border-gray-300'
                : ''}
                {disabled || mode !== 'recalling'
                ? 'cursor-default'
                : 'cursor-pointer active:scale-95'}
            "
            onclick={() => handleSquareClick(index)}
            disabled={disabled || mode !== "recalling"}
        >
            {#if mode === "feedback"}
                <span class="text-4xl">
                    {#if getSquareState(index) === "correct"}✓{/if}
                    {#if getSquareState(index) === "incorrect"}✗{/if}
                    {#if getSquareState(index) === "missed"}!{/if}
                </span>
            {/if}
        </button>
    {/each}
</div>

<style>
    .grid-square {
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    @media (min-width: 768px) {
        .grid-square {
            min-height: 100px;
        }
    }
</style>
