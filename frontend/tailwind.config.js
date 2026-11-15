/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#e8e8ee',
          100: '#c4c4d4',
          200: '#9a9ab0',
          300: '#6e6e8c',
          400: '#4a4a66',
          500: '#2a2a44',
          600: '#1a1a32',
          700: '#141428',
          800: '#0e0e20',
          900: '#08081a',
          950: '#04040e',
        },
        accent: {
          green: '#00ff9d',
          blue: '#00d4ff',
          purple: '#a855f7',
          red: '#ff3366',
          orange: '#ff9500',
          yellow: '#ffd60a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'slide-right': 'slideRight 3s linear infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'conveyor': 'conveyorMove 4s linear infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'bounce-small': 'bounceSmall 1s ease-in-out infinite',
      },
      keyframes: {
        slideRight: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(0, 255, 157, 0.3)' },
          '50%': { boxShadow: '0 0 25px rgba(0, 255, 157, 0.6)' },
        },
        conveyorMove: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(50px)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        bounceSmall: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
    },
  },
  plugins: [],
};
