type MetaEnv = Record<string, string | boolean | undefined>;

function viteEnv(): MetaEnv {
  return (import.meta as unknown as { env: MetaEnv }).env;
}

/** API base URL — Vite (`VITE_API_URL`) or Next (`NEXT_PUBLIC_API_URL`). */
export function resolveApiUrl(): string {
  const fromVite = viteEnv().VITE_API_URL;
  if (typeof fromVite === "string" && fromVite.length > 0) return fromVite;

  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  return "http://localhost:8000";
}

/** True in Vite dev or Next development builds. */
export function isStudioDev(): boolean {
  const dev = viteEnv().DEV;
  if (typeof dev === "boolean") return dev;
  return typeof process !== "undefined" && process.env.NODE_ENV !== "production";
}
