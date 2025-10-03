<script lang="ts">
    interface Props {
        children: any;
        class?: string;
    }

    let { children, class: className = "" }: Props = $props();
</script>

<div
    class="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border-4 border-white/50 {className}"
>
    {@render children()}
</div>
