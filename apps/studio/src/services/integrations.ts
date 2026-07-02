import { publishDraft as apiPublish } from "@studio/services/studio-api";
import { getHealth } from "@studio/services/governance-api";
import { getSessionToken } from "@studio/lib/auth";

export async function publishDraft(_channel: string, draftId: string) {
  return apiPublish(draftId);
}

export async function getConnectionStatus() {
  const token = getSessionToken();
  if (!token) {
    return { connected: false, label: "Not signed in" };
  }
  try {
    const api = await getHealth();
    return {
      connected: api.status === "ok",
      label: api.status === "ok" ? "API online" : "API unreachable",
    };
  } catch {
    return { connected: false, label: "API unreachable" };
  }
}
