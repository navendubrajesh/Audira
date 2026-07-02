/**
 * Audira.run design tokens — BM+UXD standing baseline (Phase 0).
 * Brand palette: professional, trust-forward, neuro-analytics accent.
 */

export const colors = {
  brand: {
    50: "#eef6ff",
    100: "#d9ebff",
    200: "#bcdcff",
    300: "#8ec5ff",
    400: "#59a3ff",
    500: "#3380ff",
    600: "#1a5ff5",
    700: "#144be1",
    800: "#173db6",
    900: "#19378f",
    950: "#142357",
  },
  neutral: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617",
  },
  success: "#059669",
  warning: "#d97706",
  danger: "#dc2626",
  heatmap: {
    low: "#e0f2fe",
    mid: "#fbbf24",
    high: "#ef4444",
  },
} as const;

export const typography = {
  fontSans: "'Inter', system-ui, -apple-system, sans-serif",
  fontMono: "'JetBrains Mono', ui-monospace, monospace",
  fontIndic: "'Noto Sans Devanagari', 'Inter', sans-serif",
} as const;

export const spacing = {
  sidebar: "16rem",
  header: "3.5rem",
} as const;

export const radii = {
  sm: "0.375rem",
  md: "0.5rem",
  lg: "0.75rem",
  xl: "1rem",
} as const;

export const productName = "Audira.run";
export const productTagline =
  "Pre-send neuro-grounded analysis for enterprise communications";
