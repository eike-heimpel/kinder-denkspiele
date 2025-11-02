<script lang="ts">
    interface Props {
        variant?: "primary" | "secondary" | "success" | "danger" | "warning";
        size?: "sm" | "md" | "lg" | "xl";
        onclick?: () => void;
        disabled?: boolean;
        class?: string;
        children: any;
    }

    let {
        variant = "primary",
        size = "md",
        onclick,
        disabled = false,
        class: className = "",
        children,
    }: Props = $props();

    const variants = {
        primary:
            "bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white shadow-lg hover:shadow-xl",
        secondary:
            "bg-white/95 hover:bg-white text-purple-700 shadow-xl hover:shadow-2xl border-4 border-white/50",
        success:
            "bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-lg hover:shadow-xl",
        danger:
            "bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 text-white shadow-lg hover:shadow-xl",
        warning:
            "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl",
    };

    const sizes = {
        sm: "px-6 py-3 text-base",
        md: "px-8 py-4 text-lg",
        lg: "px-10 py-5 text-xl",
        xl: "px-14 py-7 text-3xl",
    };
</script>

<button
    class="rounded-2xl font-black uppercase tracking-wide transition-all duration-300 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 {variants[
        variant
    ]} {sizes[size]} {className}"
    {onclick}
    {disabled}
>
    {@render children()}
</button>
