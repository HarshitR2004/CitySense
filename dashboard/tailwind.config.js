/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          750: "#1a1f35",
          850: "#0f172a",
          900: "#09090b",
        },
        acid: "#E0FF00",
        violet: "#7B00FF",
      },
      fontFamily: {
        sans: ['"JetBrains Mono"', 'monospace'],
        heading: ['"Syne"', 'sans-serif'],
      },
      boxShadow: {
        'brutal': '4px 4px 0px 0px rgba(255,255,255,1)',
        'brutal-acid': '4px 4px 0px 0px #E0FF00',
        'brutal-violet': '4px 4px 0px 0px #7B00FF',
        'brutal-sm': '2px 2px 0px 0px rgba(255,255,255,1)',
      },
      animation: {
        glow: "glow 2s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        glow: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate"), require("@tailwindcss/forms")],
}
