/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          50: "#f0f9fa",
          100: "#d9f0f2",
          500: "#0d8a99",
          600: "#0a6f7c",
          700: "#08545e",
        },
        ink: {
          900: "#101826",
          800: "#1c2635",
          600: "#48566b",
        },
        amber: {
          600: "#c2793d",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
