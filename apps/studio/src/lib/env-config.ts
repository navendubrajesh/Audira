type MetaEnv = Record<string, string | boolean | undefined>;

/** Safe read of Vite `import.meta.env` — webpack/Next may stub `import.meta` without `.env`. */
function readViteEnv(): MetaEnv {
  try {
    return (import.meta as unknown as { env?: MetaEnv }).env ?? {};
  } catch {
    return {};
  }
}

/** API base URL — Next (`NEXT_PUBLIC_API_URL`) or Vite (`VITE_API_URL`). */
export function resolveApiUrl(): string {
  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  const fromVite = readViteEnv().VITE_API_URL;
  if (typeof fromVite === "string" && fromVite.length > 0) return fromVite;

  return "http://localhost:8000";
}

/** True in Vite dev or Next development builds. */
export function isStudioDev(): boolean {
  if (typeof process !== "undefined" && process.env.NODE_ENV !== "production") {
    return true;
  }

  const dev = readViteEnv().DEV;
  return typeof dev === "boolean" ? dev : false;
}
