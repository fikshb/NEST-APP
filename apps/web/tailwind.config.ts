import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        teal: {
          700: "#2A5556",
          800: "#1C4143",
          900: "#133437",
        },
        neutral: {
          white: "#FFFFFF",
          softWhite: "#F1F1EE",
          warmBeige: "#DFDBD1",
          sand: "#D8DAD3",
        },
        text: {
          primary: "#212929",
          secondary: "#565656",
          muted: "rgba(33,41,41,0.62)",
        },
        accent: {
          goldTop: "#B4A78B",
          goldBottom: "#96856C",
          olive: "#3D4D47",
        },
        feedback: {
          success: "#2E7D32",
          warning: "#B26A00",
          danger: "#B00020",
          info: "#2B6CB0",
        },
        line: {
          DEFAULT: "rgba(33,41,41,0.10)",
          soft: "rgba(33,41,41,0.08)",
        },
      },
      fontFamily: {
        heading: ["DM Sans", "sans-serif"],
        body: ["Lora", "serif"],
        ui: ["DM Sans", "sans-serif"],
      },
      borderRadius: {
        card: "20px",
        input: "14px",
        button: "999px",
        modal: "24px",
      },
      boxShadow: {
        soft: "0 10px 30px rgba(0,0,0,0.06)",
        xs: "0 6px 18px rgba(0,0,0,0.05)",
      },
      maxWidth: {
        layout: "1200px",
      },
    },
  },
  plugins: [],
};
export default config;
