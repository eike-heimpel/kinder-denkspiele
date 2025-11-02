/**
 * Design Tokens - Kinder Denkspiele
 *
 * Centralized design system tokens for consistency across the application.
 * These tokens define colors, spacing, typography, and effects used throughout.
 *
 * Usage:
 *   import { tokens } from '$lib/design-tokens';
 *   const buttonClass = `${tokens.spacing.button.lg} ${tokens.effects.buttonHover}`;
 */

export const tokens = {
	/**
	 * Brand Colors - Purple-Pink-Blue Palette
	 * Used for backgrounds, gradients, and primary UI elements
	 */
	colors: {
		brand: {
			purple: '#c084fc', // purple-400
			purpleDark: '#a855f7', // purple-500
			pink: '#f472b6', // pink-400
			pinkDark: '#ec4899', // pink-500
			blue: '#60a5fa', // blue-400
			blueDark: '#3b82f6' // blue-500
		},

		/**
		 * Semantic colors for game cards and sections
		 */
		games: {
			verbal: {
				light: 'from-purple-50 to-pink-50',
				border: 'border-purple-200',
				text: 'text-purple-700'
			},
			visual: {
				light: 'from-blue-50 to-indigo-50',
				border: 'border-blue-200',
				text: 'text-blue-700'
			},
			reaction: {
				light: 'from-orange-50 to-red-50',
				border: 'border-orange-200',
				text: 'text-orange-700'
			},
			logic: {
				light: 'from-green-50 to-teal-50',
				border: 'border-green-200',
				text: 'text-green-700'
			},
			story: {
				light: 'from-amber-50 to-yellow-50',
				border: 'border-amber-200',
				text: 'text-amber-700'
			}
		}
	},

	/**
	 * Gradient Definitions
	 * Consistent gradient patterns used throughout the app
	 */
	gradients: {
		/** Main background gradient - purple → pink → blue */
		background: 'bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400',

		/** Navigation bar gradient with transparency */
		navbar: 'bg-gradient-to-r from-purple-500/80 via-pink-500/80 to-blue-500/80',

		/** Button gradients */
		buttons: {
			primary: 'from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600',
			success: 'from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600',
			danger: 'from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600',
			warning: 'from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
		}
	},

	/**
	 * Spacing Tokens
	 * Consistent spacing for padding, margins, and gaps
	 */
	spacing: {
		/** Card spacing */
		card: {
			padding: 'p-8',
			margin: 'mb-6',
			inner: 'mb-6',
			gap: 'gap-4'
		},

		/** Button spacing by size */
		button: {
			sm: 'px-6 py-3',
			md: 'px-8 py-4',
			lg: 'px-10 py-5',
			xl: 'px-14 py-7'
		},

		/** Page container spacing */
		container: {
			padding: 'p-2',
			topPadding: 'pt-14', // Account for fixed navbar
			maxWidth: 'max-w-4xl'
		}
	},

	/**
	 * Typography Tokens
	 * Font sizes and weights for consistency
	 */
	typography: {
		/** Heading sizes */
		heading: {
			xl: 'text-3xl font-black',
			lg: 'text-2xl font-black',
			md: 'text-xl font-bold',
			sm: 'text-lg font-bold'
		},

		/** Body text */
		body: {
			lg: 'text-lg',
			base: 'text-base',
			sm: 'text-sm'
		},

		/** Button text by size */
		button: {
			sm: 'text-base',
			md: 'text-lg',
			lg: 'text-xl',
			xl: 'text-3xl'
		},

		/** Emoji sizes */
		emoji: {
			sm: 'text-2xl',
			md: 'text-3xl',
			lg: 'text-4xl',
			xl: 'text-5xl'
		}
	},

	/**
	 * Border Radius Tokens
	 */
	radius: {
		card: 'rounded-3xl',
		button: 'rounded-2xl',
		input: 'rounded-lg',
		small: 'rounded-lg'
	},

	/**
	 * Shadow Effects
	 */
	shadows: {
		card: 'shadow-lg hover:shadow-xl',
		button: 'shadow-lg hover:shadow-xl',
		navbar: 'shadow-xl hover:shadow-2xl',
		strong: 'shadow-2xl',
		text: 'drop-shadow-lg'
	},

	/**
	 * Animation & Transition Effects
	 */
	effects: {
		/** Button hover effects */
		buttonHover: 'transition-all duration-300 transform hover:scale-105 active:scale-95',

		/** Card hover effects */
		cardHover: 'transition-all duration-300',

		/** Backdrop blur for glassmorphism */
		blur: {
			sm: 'backdrop-blur-sm',
			md: 'backdrop-blur-md',
			lg: 'backdrop-blur-lg'
		},

		/** Fade in animation */
		fadeIn: 'animate-fade-in',

		/** Gradient animation */
		gradientAnimate: 'animate-gradient'
	},

	/**
	 * Border Styles
	 */
	borders: {
		card: 'border-4',
		button: {
			default: '',
			white: 'border-4 border-white/50'
		}
	},

	/**
	 * Z-Index Layers
	 */
	zIndex: {
		navbar: 'z-50',
		modal: 'z-50',
		dropdown: 'z-40'
	}
} as const;

/**
 * Helper to combine token classes
 *
 * @example
 * const cardClass = combine(
 *   tokens.spacing.card.padding,
 *   tokens.radius.card,
 *   tokens.shadows.card
 * );
 */
export function combine(...classes: string[]): string {
	return classes.filter(Boolean).join(' ');
}

/**
 * Predefined Component Class Combinations
 * Common class combinations for frequently used patterns
 */
export const components = {
	/** Standard game card styling */
	gameCard: combine(
		tokens.radius.card,
		tokens.spacing.card.padding,
		tokens.spacing.card.margin,
		tokens.borders.card,
		tokens.shadows.card,
		tokens.effects.cardHover
	),

	/** Standard button base (add variant gradient separately) */
	button: combine(
		tokens.radius.button,
		'font-black uppercase tracking-wide',
		tokens.effects.buttonHover,
		'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100'
	),

	/** Navigation bar */
	navbar: combine(
		'fixed top-0 left-0 right-0',
		tokens.zIndex.navbar,
		tokens.gradients.navbar,
		tokens.effects.blur.md,
		'px-2 py-2 flex items-center justify-between'
	),

	/** Main page container */
	pageContainer: combine(
		'min-h-screen',
		tokens.gradients.background,
		tokens.spacing.container.padding
	),

	/** Content wrapper (accounts for navbar) */
	contentWrapper: combine(
		tokens.spacing.container.maxWidth,
		'mx-auto',
		tokens.spacing.container.topPadding
	)
} as const;
