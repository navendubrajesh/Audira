// TODO(TCA-011): Channel publish integrations
export async function publishDraft(_channel: string, _draftId: string) {
  await new Promise((r) => setTimeout(r, 300));
  return { queued: true, message: "Publish queued (mock)" };
}

// TODO(TCA-067): SSO connection status
export async function getConnectionStatus() {
  return { connected: true, label: "All integrations nominal" };
}
