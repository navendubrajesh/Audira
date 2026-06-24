import type { Config } from "tailwindcss";
import { colors, typography, radii } from "@resonode/design-tokens";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: colors.brand,
        neutral: colors.neutral,
        success: colors.success,
        warning: colors.warning,
        danger: colors.danger,
      },
      fontFamily: {
        sans: typography.fontSans.split(",").map((f) => f.trim()),
        indic: typography.fontIndic.split(",").map((f) => f.trim()),
      },
      borderRadius: radii,
    },
  },
  plugins: [],
};

export default config;
