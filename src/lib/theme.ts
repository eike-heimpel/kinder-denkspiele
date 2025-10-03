export const theme = {
    colors: {
        // Primary brand colors
        primary: {
            50: '#f0f9ff',
            100: '#e0f2fe',
            200: '#bae6fd',
            300: '#7dd3fc',
            400: '#38bdf8',
            500: '#0ea5e9',
            600: '#0284c7',
            700: '#0369a1',
            800: '#075985',
            900: '#0c4a6e',
        },
        // Success/correct colors
        success: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e',
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
        },
        // Warning/hard mode colors
        warning: {
            50: '#fff7ed',
            100: '#ffedd5',
            200: '#fed7aa',
            300: '#fdba74',
            400: '#fb923c',
            500: '#f97316',
            600: '#ea580c',
            700: '#c2410c',
            800: '#9a3412',
            900: '#7c2d12',
        },
        // Danger/error colors
        danger: {
            50: '#fef2f2',
            100: '#fee2e2',
            200: '#fecaca',
            300: '#fca5a5',
            400: '#f87171',
            500: '#ef4444',
            600: '#dc2626',
            700: '#b91c1c',
            800: '#991b1b',
            900: '#7f1d1d',
        },
        // Purple accent
        purple: {
            50: '#faf5ff',
            100: '#f3e8ff',
            200: '#e9d5ff',
            300: '#d8b4fe',
            400: '#c084fc',
            500: '#a855f7',
            600: '#9333ea',
            700: '#7e22ce',
            800: '#6b21a8',
            900: '#581c87',
        },
        // Neutral grays
        gray: {
            50: '#f9fafb',
            100: '#f3f4f6',
            200: '#e5e7eb',
            300: '#d1d5db',
            400: '#9ca3af',
            500: '#6b7280',
            600: '#4b5563',
            700: '#374151',
            800: '#1f2937',
            900: '#111827',
        },
    },
    
    gradients: {
        home: 'from-purple-400 via-pink-400 to-blue-400',
        game: 'from-indigo-500 via-purple-500 to-pink-500',
        success: 'from-green-400 to-emerald-500',
        danger: 'from-red-400 to-rose-500',
        primary: 'from-blue-400 to-cyan-500',
        warm: 'from-orange-400 via-red-400 to-pink-500',
    },
    
    shadows: {
        sm: 'shadow-sm',
        md: 'shadow-md',
        lg: 'shadow-lg',
        xl: 'shadow-xl',
        '2xl': 'shadow-2xl',
        inner: 'shadow-inner',
        glow: 'shadow-[0_0_30px_rgba(168,85,247,0.4)]',
        glowSuccess: 'shadow-[0_0_30px_rgba(34,197,94,0.4)]',
        glowDanger: 'shadow-[0_0_30px_rgba(239,68,68,0.4)]',
    },
    
    animations: {
        bounce: 'animate-bounce',
        pulse: 'animate-pulse',
        spin: 'animate-spin',
        ping: 'animate-ping',
        wiggle: 'animate-wiggle',
    },
    
    spacing: {
        buttonPadding: {
            sm: 'px-4 py-2',
            md: 'px-6 py-3',
            lg: 'px-8 py-4',
            xl: 'px-12 py-6',
        },
        cardPadding: 'p-8',
        gap: {
            sm: 'gap-2',
            md: 'gap-4',
            lg: 'gap-6',
            xl: 'gap-8',
        },
    },
    
    text: {
        size: {
            xs: 'text-xs',
            sm: 'text-sm',
            base: 'text-base',
            lg: 'text-lg',
            xl: 'text-xl',
            '2xl': 'text-2xl',
            '3xl': 'text-3xl',
            '4xl': 'text-4xl',
            '5xl': 'text-5xl',
            '6xl': 'text-6xl',
            '7xl': 'text-7xl',
            '8xl': 'text-8xl',
            '9xl': 'text-9xl',
        },
        weight: {
            normal: 'font-normal',
            medium: 'font-medium',
            semibold: 'font-semibold',
            bold: 'font-bold',
            extrabold: 'font-extrabold',
            black: 'font-black',
        },
    },
    
    borders: {
        radius: {
            sm: 'rounded-sm',
            md: 'rounded-md',
            lg: 'rounded-lg',
            xl: 'rounded-xl',
            '2xl': 'rounded-2xl',
            '3xl': 'rounded-3xl',
            full: 'rounded-full',
        },
        width: {
            0: 'border-0',
            2: 'border-2',
            4: 'border-4',
            8: 'border-8',
        },
    },
    
    transitions: {
        all: 'transition-all duration-300 ease-in-out',
        fast: 'transition-all duration-150 ease-in-out',
        slow: 'transition-all duration-500 ease-in-out',
        colors: 'transition-colors duration-300 ease-in-out',
        transform: 'transition-transform duration-300 ease-in-out',
    },
};

// Helper function to get theme values
export function getTheme() {
    return theme;
}
