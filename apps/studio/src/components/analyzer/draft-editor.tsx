import { useEffect, useRef } from "react";

import { cn } from "@studio/lib/utils";

interface DraftEditorProps {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  highlightStart?: number | null;
  highlightEnd?: number | null;
  className?: string;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function buildHighlightHtml(
  text: string,
  start: number | null | undefined,
  end: number | null | undefined,
): string {
  const safe = escapeHtml(text);
  if (start == null || end == null || start >= end) return safe;
  const s = Math.max(0, Math.min(start, text.length));
  const e = Math.max(s, Math.min(end, text.length));
  return (
    escapeHtml(text.slice(0, s)) +
    `<mark class="bg-accent/30 text-inherit rounded-sm">${escapeHtml(text.slice(s, e))}</mark>` +
    escapeHtml(text.slice(e))
  );
}

// TODO(TCA-092): Replace textarea with rich markdown editor + code-block toolbar
export function DraftEditor({
  id = "draft-editor",
  value,
  onChange,
  highlightStart,
  highlightEnd,
  className,
}: DraftEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);

  const syncScroll = () => {
    if (textareaRef.current && backdropRef.current) {
      backdropRef.current.scrollTop = textareaRef.current.scrollTop;
      backdropRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  useEffect(() => {
    if (highlightStart != null && highlightEnd != null && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(highlightStart, highlightEnd);
      syncScroll();
    }
  }, [highlightStart, highlightEnd]);

  return (
    <div className={cn("relative min-h-0 flex-1", className)}>
      <div
        ref={backdropRef}
        aria-hidden
        className="pointer-events-none absolute inset-0 overflow-auto whitespace-pre-wrap break-words p-4 font-mono text-sm leading-relaxed text-transparent"
        dangerouslySetInnerHTML={{
          __html: buildHighlightHtml(value, highlightStart, highlightEnd),
        }}
      />
      <label className="sr-only" htmlFor={id}>
        Draft editor
      </label>
      <textarea
        ref={textareaRef}
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onScroll={syncScroll}
        className="absolute inset-0 resize-none bg-transparent p-4 font-mono text-sm leading-relaxed caret-slate-900 focus:outline-none dark:caret-slate-100"
        spellCheck
      />
    </div>
  );
}
