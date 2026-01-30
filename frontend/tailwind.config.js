/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Clean, ChatGPT-inspired palette
        primary: '#10A37F',        // ChatGPT green
        'primary-hover': '#0F8A6C',
        'primary-light': '#E6F6F1',
        'primary-dark': '#0F6F55',

        secondary: '#0F766E',      // Deep teal
        'secondary-light': '#E6F6F4',

        accent: '#1F2937',         // Slate for emphasis
        'accent-dark': '#111827',

        coral: '#14B8A6',          // Teal (used in gradients)
        lavender: '#94A3B8',       // Slate
        peach: '#CBD5E1',          // Light slate

        // Extended palette (toned down)
        teal: '#0F766E',
        'teal-light': '#E6F6F4',
        rose: '#F43F5E',
        'rose-light': '#FFE4E6',
        indigo: '#6366F1',
        'indigo-light': '#EEF2FF',
        amber: '#F59E0B',
        'amber-light': '#FEF3C7',
        emerald: '#059669',
        'emerald-light': '#D1FAE5',
        violet: '#8B5CF6',
        'violet-light': '#EDE9FE',

        background: '#F7F7F8',
        'background-alt': '#F1F5F9',
        surface: '#FFFFFF',
        'surface-warm': '#FFFFFF',

        'text-deep': '#0F172A',
        'text-muted': '#475569',
        'text-light': '#94A3B8',

        border: '#E2E8F0',
        'border-light': '#F1F5F9',

        success: '#16A34A',
        danger: '#DC2626',
        warning: '#F59E0B',
      },
      fontFamily: {
        display: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        hebrew: ['Heebo', 'Arial', 'sans-serif'],
      },
      borderRadius: {
        'blob': '60% 40% 30% 70% / 60% 30% 70% 40%',
        'blob-2': '30% 70% 70% 30% / 30% 52% 48% 70%',
        'organic': '20px 60px 40px 80px',
        '4xl': '1.5rem',
        '5xl': '2rem',
      },
      boxShadow: {
        'card': '0 1px 2px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.06)',
        'card-hover': '0 2px 6px rgba(15, 23, 42, 0.08), 0 12px 30px rgba(15, 23, 42, 0.08)',
        'button': '0 1px 2px rgba(15, 23, 42, 0.12)',
        'soft': '0 1px 3px rgba(15, 23, 42, 0.08)',
        'glow': '0 0 24px rgba(16, 163, 127, 0.2)',
        'glow-secondary': '0 0 24px rgba(15, 118, 110, 0.2)',
        'inner-glow': 'inset 0 1px 8px rgba(255, 255, 255, 0.4)',
      },
      screens: {
        'xs': '375px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        'touch': { 'raw': '(hover: none) and (pointer: coarse)' },
        'no-touch': { 'raw': '(hover: hover) and (pointer: fine)' },
        'landscape': { 'raw': '(orientation: landscape)' },
        'portrait': { 'raw': '(orientation: portrait)' },
        'short': { 'raw': '(max-height: 600px)' },
        'tall': { 'raw': '(min-height: 700px)' },
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      height: {
        'screen-dvh': '100dvh',
        'screen-svh': '100svh',
        'screen-lvh': '100lvh',
      },
      minHeight: {
        'screen-dvh': '100dvh',
        'screen-svh': '100svh',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out infinite 2s',
        'breathe': 'breathe 4s ease-in-out infinite',
        'pulse-soft': 'pulse-soft 3s ease-in-out infinite',
        'slide-up': 'slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-down': 'slide-down 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'scale-in': 'scale-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'fade-in': 'fade-in 0.6s ease-out forwards',
        'heart-beat': 'heart-beat 0.8s ease-in-out',
        'bounce-soft': 'bounce-soft 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'wiggle': 'wiggle 0.5s ease-in-out',
        'blob': 'blob 10s ease-in-out infinite',
        'blob-reverse': 'blob 12s ease-in-out infinite reverse',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 8s linear infinite',
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'shrink-width': 'shrink-width linear forwards',
      },
      keyframes: {
        'float': {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '33%': { transform: 'translateY(-10px) rotate(1deg)' },
          '66%': { transform: 'translateY(-5px) rotate(-1deg)' },
        },
        'breathe': {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.8' },
          '50%': { transform: 'scale(1.05)', opacity: '1' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(0.98)' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(30px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-30px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'heart-beat': {
          '0%': { transform: 'scale(1)' },
          '15%': { transform: 'scale(1.25)' },
          '30%': { transform: 'scale(1)' },
          '45%': { transform: 'scale(1.15)' },
          '60%': { transform: 'scale(1)' },
        },
        'bounce-soft': {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'wiggle': {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(-3deg)' },
          '75%': { transform: 'rotate(3deg)' },
        },
        'blob': {
          '0%, 100%': { borderRadius: '60% 40% 30% 70% / 60% 30% 70% 40%' },
          '25%': { borderRadius: '30% 60% 70% 40% / 50% 60% 30% 60%' },
          '50%': { borderRadius: '50% 60% 30% 60% / 30% 40% 70% 60%' },
          '75%': { borderRadius: '60% 40% 60% 30% / 70% 30% 50% 60%' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'shrink-width': {
          '0%': { width: '100%' },
          '100%': { width: '0%' },
        },
      },
      backgroundImage: {
        'gradient-warm': 'linear-gradient(135deg, #10A37F 0%, #0F766E 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #0F766E 0%, #10A37F 100%)',
        'gradient-ocean': 'linear-gradient(135deg, #0F766E 0%, #14B8A6 100%)',
        'gradient-mesh': 'radial-gradient(at 40% 20%, #E6F6F1 0px, transparent 50%), radial-gradient(at 80% 0%, #E6F6F4 0px, transparent 50%), radial-gradient(at 0% 50%, #F1F5F9 0px, transparent 50%)',
      },
    },
  },
  plugins: [],
}
