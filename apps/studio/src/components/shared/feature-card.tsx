import { BacklogStatusBadge, StoryIdBadge } from "@studio/components/ui/badge";
import { storyById } from "@studio/mock/fixtures";
import type { BacklogStory } from "@studio/types";
import { cn } from "@studio/lib/utils";

export function FeatureCard({
  storyId,
  title,
  description,
  className,
}: {
  storyId: string;
  title?: string;
  description?: string;
  className?: string;
}) {
  const story: BacklogStory | undefined = storyById(storyId);

  return (
    <article
      className={cn(
        "rounded-lg border border-border bg-surface-raised p-4 shadow-card",
        className,
      )}
    >
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <StoryIdBadge id={storyId} />
        {story ? <BacklogStatusBadge status={story.Status} /> : null}
        {story?.Phase.includes("Phase 3") ? (
          <span className="text-[10px] font-semibold uppercase text-accent">Coming soon</span>
        ) : null}
      </div>
      <h3 className="font-display text-sm font-semibold">
        {title ?? story?.Functionality ?? storyId}
      </h3>
      <p className="mt-1 text-xs text-muted-foreground line-clamp-3">
        {description ?? story?.["User Story"] ?? "Backlog placeholder"}
      </p>
      {story ? (
        <p className="mt-2 text-[11px] text-muted-foreground">
          {story.Epic.split(" ").slice(0, 1)[0]} · {story.Priority} · {story.Role}
        </p>
      ) : null}
    </article>
  );
}

export function FeatureGrid({ storyIds }: { storyIds: string[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {storyIds.map((id) => (
        <FeatureCard key={id} storyId={id} />
      ))}
    </div>
  );
}
