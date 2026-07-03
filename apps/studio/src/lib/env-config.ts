type MetaEnv = Record<string, string | boolean | undefined>;

/** Safe read of Vite `import.meta.env` — webpack/Next may stub `import.meta` without `.env`. */
function readViteEnv(): MetaEnv {
  try {
    return (import.meta as unknown as { env?: MetaEnv }).env ?? {};
  } catch {
    return {};
  }
}

function configuredApiUrl(): string {
  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  const fromVite = readViteEnv().VITE_API_URL;
  if (typeof fromVite === "string" && fromVite.length > 0) return fromVite;

  return "http://localhost:8000";
}

/** External API URL — OAuth redirects must hit the API host directly. */
export function resolveOAuthApiUrl(): string {
  return configuredApiUrl();
}

/** API URL for browser fetch — same-origin proxy when API is cross-origin (avoids CORS). */
export function resolveFetchApiUrl(): string {
  const configured = configuredApiUrl();
  if (typeof window !== "undefined") {
    try {
      const apiOrigin = new URL(configured).origin;
      if (apiOrigin !== window.location.origin) {
        return "/backend";
      }
    } catch {
      // use configured value
    }
  }
  return configured;
}

/** @deprecated Prefer resolveFetchApiUrl or resolveOAuthApiUrl. */
export function resolveApiUrl(): string {
  return resolveFetchApiUrl();
}
/** True in Vite dev or Next development builds. */
export function isStudioDev(): boolean {
  if (typeof process !== "undefined" && process.env.NODE_ENV !== "production") {
    return true;
  }

  const dev = readViteEnv().DEV;
  return typeof dev === "boolean" ? dev : false;
}
