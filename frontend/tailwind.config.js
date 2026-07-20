/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0D16',
        glass: 'rgba(17,24,39,0.55)',
        'glass-hover': 'rgba(24,32,51,0.7)',
        border: 'rgba(249,250,251,0.09)',
        'border-hover': 'rgba(129,140,248,0.4)',
        primary: '#6366F1',
        'primary-soft': '#818CF8',
        accent: '#22D3EE',
        text: '#F9FAFB',
        'text-dim': '#9CA3AF',
        'text-faint': '#64707F',
        success: '#34D399',
        warn: '#FBBF24',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '12px',
      },
    },
  },
  plugins: [],
}
