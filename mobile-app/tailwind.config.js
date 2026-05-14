/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,jsx,ts,tsx}', './components/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0a0e27',
          800: '#0f1935',
          700: '#1a2a4a',
        },
        glow: {
          cyan: '#00d9ff',
          blue: '#0099ff',
          light: 'rgba(0, 217, 255, 0.2)',
        },
      },
      boxShadow: {
        glow: '0 0 20px rgba(0, 217, 255, 0.3)',
        'glow-sm': '0 0 10px rgba(0, 217, 255, 0.2)',
        'glow-lg': '0 0 30px rgba(0, 217, 255, 0.4)',
      },
      borderRadius: {
        premium: '20px',
      },
    },
  },
  plugins: [],
};
