<script lang="ts">
    interface Props {
        variant?: "primary" | "secondary" | "success" | "danger";
        size?: "sm" | "md" | "lg" | "xl";
        onclick?: () => void;
        disabled?: boolean;
        children: any;
    }

    let {
        variant = "primary",
        size = "md",
        onclick,
        disabled = false,
        children,
    }: Props = $props();

    const variants = {
        primary: "bg-blue-500 hover:bg-blue-600 text-white",
        secondary: "bg-gray-500 hover:bg-gray-600 text-white",
        success: "bg-green-500 hover:bg-green-600 text-white",
        danger: "bg-red-500 hover:bg-red-600 text-white",
    };

    const sizes = {
        sm: "px-4 py-2 text-sm",
        md: "px-6 py-3 text-base",
        lg: "px-8 py-4 text-lg",
        xl: "px-12 py-6 text-2xl",
    };
</script>

<button
    class="rounded-xl font-bold transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed {variants[
        variant
    ]} {sizes[size]}"
    {onclick}
    {disabled}
>
    {@render children()}
</button>
