import { MessageSquare, ShieldAlert } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@studio/components/ui/button";
import { ScoreChip } from "@studio/components/ui/score-chip";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import {
  checkCommentGuardrail,
  draftComment,
  listEngagementQueue,
  type EngagementPost,
} from "@studio/services/studio-api";

export function EngagementHelperPage() {
  const [queue, setQueue] = useState<EngagementPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [guardrail, setGuardrail] = useState<{ passed: boolean; message: string } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const items = await listEngagementQueue();
      setQueue(items);
      setSelected(items[0]?.id ?? null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const post = queue.find((p) => p.id === selected);

  useEffect(() => {
    if (!post) return;
    void draftComment(post.id).then((r) => {
      setComment(r.comment);
      void checkCommentGuardrail(r.comment).then(setGuardrail);
    });
  }, [post?.id]);

  if (loading) return <GlobalStatePanel variant="loading" />;

  return (
    <div className="flex h-full">
      <div className="w-80 shrink-0 overflow-y-auto border-r border-border p-4">
        <h2 className="font-display text-sm font-semibold">Peer-post queue</h2>
        <StoryIdBadge id="TCA-088" />
        <ul className="mt-3 space-y-2">
          {queue.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => setSelected(item.id)}
                className={`w-full rounded-lg border p-3 text-left text-sm ${
                  selected === item.id ? "border-primary bg-primary/5" : "border-border"
                }`}
              >
                <p className="font-medium">{item.author}</p>
                <p className="line-clamp-2 text-xs text-muted-foreground">{item.title}</p>
                <ScoreChip score={item.relevance / 10} max={10} className="mt-2" />
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="flex-1 overflow-y-auto p-6">
        <h2 className="font-display text-lg font-semibold">Comment helper</h2>
        {post ? (
          <>
            <p className="mt-1 text-sm text-muted-foreground">Re: {post.title}</p>
            <div className="mt-4 rounded-lg border border-border bg-surface-raised p-4">
              <div className="mb-2 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-primary" />
                <span className="text-sm font-semibold">Counter-perspective draft</span>
                <StoryIdBadge id="TCA-089" />
              </div>
              <textarea
                className="w-full rounded-md border border-border bg-surface p-3 text-sm leading-relaxed"
                rows={5}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                onBlur={() => void checkCommentGuardrail(comment).then(setGuardrail)}
              />
            </div>
            {guardrail ? (
              <div
                className={`mt-3 flex items-start gap-2 rounded-lg border p-3 text-xs ${
                  guardrail.passed
                    ? "border-success/30 bg-success/10"
                    : "border-warning/30 bg-warning/10"
                }`}
              >
                <ShieldAlert className="h-4 w-4 shrink-0" />
                <div>
                  <strong>Tone guardrail (TCA-090):</strong> {guardrail.message}
                </div>
              </div>
            ) : null}
            <Button
              className="mt-4"
              onClick={() => navigator.clipboard.writeText(comment)}
            >
              Copy to clipboard
            </Button>
          </>
        ) : null}
      </div>
    </div>
  );
}
