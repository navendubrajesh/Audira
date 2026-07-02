import { MessageSquare, ShieldAlert } from "lucide-react";
import { useState } from "react";

import { FeatureGrid } from "@/components/shared/feature-card";
import { Button } from "@/components/ui/button";
import { ScoreChip } from "@/components/ui/score-chip";
import { StoryIdBadge } from "@/components/ui/badge";
import { engagementQueue } from "@/mock/fixtures";

// TODO(TCA-088): Peer-post relevance ranker with live LinkedIn feed stub
// TODO(TCA-089): Counter-perspective comment draftsman
// TODO(TCA-090): Tone & authority guardrail for comments
export function EngagementHelperPage() {
  const [selected, setSelected] = useState(engagementQueue[0]?.id);
  const post = engagementQueue.find((p) => p.id === selected);

  return (
    <div className="flex h-full">
      <div className="w-80 shrink-0 border-r border-border overflow-y-auto p-4">
        <h2 className="font-display text-sm font-semibold">Peer-post queue</h2>
        <StoryIdBadge id="TCA-088" />
        <ul className="mt-3 space-y-2">
          {engagementQueue.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => setSelected(item.id)}
                className={`w-full rounded-lg border p-3 text-left text-sm ${
                  selected === item.id ? "border-primary bg-primary/5" : "border-border"
                }`}
              >
                <p className="font-medium">{item.author}</p>
                <p className="text-xs text-muted-foreground line-clamp-2">{item.title}</p>
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
              <p className="text-sm leading-relaxed">
                Appreciate the eval-pipeline framing, {post.author.split(" ")[0]}. We saw similar
                gaps when scoring internal town-hall decks — emotion signal collapsed when slides
                exceeded 12-word headlines. Curious if you controlled for slide density in your
                benchmark?
              </p>
            </div>
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-warning/30 bg-warning/10 p-3 text-xs">
              <ShieldAlert className="h-4 w-4 shrink-0 text-warning" />
              <div>
                <strong>Tone guardrail (TCA-090):</strong> Assertiveness within authority band —
                avoid dismissive phrasing toward peer.
              </div>
            </div>
            <Button className="mt-4">Copy to clipboard</Button>
          </>
        ) : null}
        <div className="mt-8">
          <FeatureGrid storyIds={["TCA-088", "TCA-089", "TCA-090"]} />
        </div>
      </div>
    </div>
  );
}
