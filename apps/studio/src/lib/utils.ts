import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function scoreTone(value: number, max = 10): "success" | "warning" | "danger" {
  const pct = (value / max) * 100;
  if (pct >= 75) return "success";
  if (pct >= 50) return "warning";
  return "danger";
}

export function scoreToneClass(tone: "success" | "warning" | "danger"): string {
  return {
    success: "text-success bg-success/10 border-success/30",
    warning: "text-warning bg-warning/10 border-warning/30",
    danger: "text-danger bg-danger/10 border-danger/30",
  }[tone];
}
