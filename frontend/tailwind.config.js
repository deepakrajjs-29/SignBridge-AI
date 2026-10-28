/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "page-bg": "var(--bg-main, #F5F3ED)",
        "midnight": "var(--card-bg, #0f172a)",
        "midnight-light": "var(--card-elevated, #1e293b)",
        "midnight-dark": "var(--bg-main, #070c18)",
        "teal-deep": "var(--color-primary, #123C43)",
        "deep-teal": "var(--color-primary, #123C43)",
        "deep-teal-hover": "var(--color-primary-hover, #0d2e34)",
        "seafoam": "var(--color-accent, #62B6A5)",
        "seafoam-light": "var(--color-accent-light, #E9F6F3)",
        "amber-muted": "var(--color-accent, #D9A76C)",
        "card-border": "var(--border-color, #E2DFD6)",
        "text-secondary": "#667570",
        "muted-text": "#667570",
        "soft-surface": "var(--soft-bg, #FAF8F5)",
        "surface-white": "var(--card-bg, #FFFFFF)",
        "sidebar-hover": "rgba(255, 255, 255, 0.07)",
        brand: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0284c7",
          600: "#0369a1",
          700: "#075985",
          800: "#0c4a6e",
          900: "#082f49",
        },
        isl: {
          teal: "#123C43",
          cyan: "#62B6A5",
          emerald: "#62B6A5",
        }
      },
      fontFamily: {
        sans: [
          "'Plus Jakarta Sans'",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
