// tailwind.config.ts
const config = {
  theme: {
    extend: {
      colors: {
        atc: {
          background: "#020617", // Deep Slate-950
          sidebar: "#0f172a",    // Slate-900
          card: "#1e293b",       // Slate-800
          alert: "#ef4444",      // High-vis Red
          warning: "#fbbf24",    // ATC Amber
          active: "#34d399",     // Emerald Green
          muted: "#94a3b8",      // Muted Slate for timestamps
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular"],
        sans: ["Inter", "sans-serif"],
      },
    },
  },
};