import type { ModuleId } from "@studio/types";

export function analysisContextForModule(module: ModuleId): {
  artifact_type_code: string;
  channel: string;
  objective: "inform" | "engage" | "drive_action" | "reassure" | "celebrate";
} {
  switch (module) {
    case "linkedin":
      return { artifact_type_code: "press_release", channel: "press", objective: "engage" };
    case "social":
      return { artifact_type_code: "intranet", channel: "video", objective: "engage" };
    case "placement":
      return { artifact_type_code: "policy", channel: "email", objective: "drive_action" };
    case "blog":
      return { artifact_type_code: "intranet", channel: "intranet", objective: "inform" };
    default:
      return { artifact_type_code: "email", channel: "email", objective: "engage" };
  }
}
