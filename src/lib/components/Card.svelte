<script lang="ts">
    interface Props {
        children: any;
        class?: string;
    }

    let { children, class: className = "" }: Props = $props();
</script>

<div class="bg-white rounded-2xl shadow-lg p-6 {className}">
    {@render children()}
</div>
