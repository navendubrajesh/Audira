import { FileCode2, Image, Upload } from "lucide-react";
import { useCallback, useState } from "react";

import { StoryIdBadge } from "@studio/components/ui/badge";
import { useAnalyzerStore } from "@studio/store/analyzer-store";

// TODO(TCA-079): Route uploads to asset library with type detection (image/code/diagram)
// TODO(TCA-004): Block engineering-only artifacts per taxonomy
export function MultimodalDropZone() {
  const { attachedAssets, addAsset } = useAnalyzerStore();
  const [dragOver, setDragOver] = useState(false);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) addAsset(file.name);
    },
    [addAsset],
  );

  return (
    <div className="rounded-lg border border-dashed border-border bg-surface-overlay/50 p-3">
      <div className="mb-2 flex items-center gap-2">
        <Upload className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium">Multimodal assets</span>
        <StoryIdBadge id="TCA-079" />
      </div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`rounded-md border-2 border-dashed p-4 text-center text-xs transition ${
          dragOver ? "border-primary bg-primary/5" : "border-transparent"
        }`}
      >
        Drop diagram, screenshot, or code snippet
      </div>
      <ul className="mt-2 space-y-1">
        {attachedAssets.map((name) => (
          <li
            key={name}
            className="flex items-center gap-2 rounded-md bg-surface-raised px-2 py-1 text-xs"
          >
            {name.endsWith(".png") || name.endsWith(".jpg") ? (
              <Image className="h-3.5 w-3.5 text-accent" />
            ) : (
              <FileCode2 className="h-3.5 w-3.5 text-primary" />
            )}
            {name}
          </li>
        ))}
      </ul>
    </div>
  );
}
