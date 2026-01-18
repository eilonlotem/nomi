/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Rich, warm palette - vibrant and distinctive
        primary: '#D96852',        // Rich terracotta - bolder
        'primary-hover': '#C45A45',
        'primary-light': '#FFE8E3',
        'primary-dark': '#B84D39',
        
        secondary: '#4AA488',      // Deep sage - richer green
        'secondary-light': '#D5EFE6',
        
        accent: '#E8A848',         // Rich golden amber
        'accent-dark': '#C78B2D',
        
        coral: '#FF7B6B',          // Vibrant coral
        lavender: '#9B8DC2',       // Rich lavender
        peach: '#FFB896',          // Warm peach
        
        // Extended palette for variety
        teal: '#32A89C',           // Ocean teal
        'teal-light': '#D8F3F0',
        rose: '#E85A7A',           // Rose pink
        'rose-light': '#FFEAEF',
        indigo: '#6366F1',         // Electric indigo
        'indigo-light': '#EEF0FF',
        amber: '#F59E0B',          // Warm amber
        'amber-light': '#FEF3C7',
        emerald: '#059669',        // Deep emerald
        'emerald-light': '#D1FAE5',
        violet: '#8B5CF6',         // Rich violet
        'violet-light': '#EDE9FE',
        
        background: '#FDF8F3',     // Warm cream
        'background-alt': '#F5EDE6',
        surface: '#FFFFFF',
        'surface-warm': '#FFFAF7',
        
        'text-deep': '#1F2937',
        'text-muted': '#6B7280',
        'text-light': '#9CA3AF',
        
        border: '#E8DED5',
        'border-light': '#F3EDE7',
        
        success: '#059669',
        danger: '#DC2626',
        warning: '#F59E0B',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Heebo', 'DM Sans', 'system-ui', '-apple-system', 'sans-serif'],
        hebrew: ['Heebo', 'Arial', 'sans-serif'],
      },
      borderRadius: {
        'blob': '60% 40% 30% 70% / 60% 30% 70% 40%',
        'blob-2': '30% 70% 70% 30% / 30% 52% 48% 70%',
        'organic': '20px 60px 40px 80px',
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      boxShadow: {
        'card': '0 8px 32px -8px rgba(224, 122, 95, 0.15)',
        'card-hover': '0 12px 40px -8px rgba(224, 122, 95, 0.25)',
        'button': '0 4px 16px -2px rgba(224, 122, 95, 0.4)',
        'soft': '0 4px 20px -4px rgba(0, 0, 0, 0.08)',
        'glow': '0 0 40px rgba(224, 122, 95, 0.3)',
        'glow-secondary': '0 0 40px rgba(129, 178, 154, 0.3)',
        'inner-glow': 'inset 0 2px 20px rgba(255, 255, 255, 0.5)',
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
      },
      backgroundImage: {
        'gradient-warm': 'linear-gradient(135deg, #E07A5F 0%, #F2CC8F 50%, #81B29A 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #F4978E 0%, #E07A5F 50%, #F2CC8F 100%)',
        'gradient-ocean': 'linear-gradient(135deg, #81B29A 0%, #B8A9C9 100%)',
        'gradient-mesh': 'radial-gradient(at 40% 20%, #FAE5E0 0px, transparent 50%), radial-gradient(at 80% 0%, #D8EBE2 0px, transparent 50%), radial-gradient(at 0% 50%, #F2CC8F33 0px, transparent 50%)',
      },
    },
  },
  plugins: [],
}
