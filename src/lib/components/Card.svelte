<script lang="ts">
    interface Props {
        children: any;
        class?: string;
    }

    let { children, class: className = "" }: Props = $props();
</script>

<div
    class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl p-4 border-2 border-white/50 {className}"
>
    {@render children()}
</div>
