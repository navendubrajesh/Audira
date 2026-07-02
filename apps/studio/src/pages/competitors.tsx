import { useMemo, useState } from "react";

import { BacklogStatusBadge } from "@studio/components/ui/badge";
import { competitors, backlogStories } from "@studio/mock/fixtures";

export function CompetitorLandscapePage() {
  const [filter, setFilter] = useState("");
  const [archetype, setArchetype] = useState("All");

  const rows = useMemo(() => {
    return competitors.filter((c) => {
      const matchFilter =
        !filter ||
        c.Vendor.toLowerCase().includes(filter.toLowerCase()) ||
        c["Signature strength / signal"].toLowerCase().includes(filter.toLowerCase());
      const matchArchetype =
        archetype === "All" || c["Primary Archetype"].includes(archetype);
      return matchFilter && matchArchetype;
    });
  }, [filter, archetype]);

  const archetypes = [
    "All",
    ...new Set(competitors.map((c) => c["Primary Archetype"].split(".")[0])),
  ];

  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Competitor Landscape</h1>
      <p className="text-sm text-muted-foreground">
        Live data from backlog spreadsheet — {competitors.length} vendors
      </p>

      <div className="mt-4 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Filter vendors…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="h-9 rounded-lg border border-border bg-surface-raised px-3 text-sm"
          aria-label="Filter competitors"
        />
        <select
          value={archetype}
          onChange={(e) => setArchetype(e.target.value)}
          className="h-9 rounded-lg border border-border bg-surface-raised px-3 text-sm"
          aria-label="Filter by archetype"
        >
          {archetypes.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-4 overflow-x-auto rounded-lg border border-border">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="bg-surface-overlay text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Vendor</th>
              <th className="px-4 py-3">Archetype</th>
              <th className="px-4 py-3">Modalities</th>
              <th className="px-4 py-3">Core metrics</th>
              <th className="px-4 py-3">Enterprise fit</th>
              <th className="px-4 py-3">Signal</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.Vendor} className="border-t border-border hover:bg-surface-overlay/50">
                <td className="px-4 py-3 font-medium">
                  <a
                    href={`https://${row.Website}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary hover:underline"
                  >
                    {row.Vendor}
                  </a>
                </td>
                <td className="px-4 py-3 text-xs">{row["Primary Archetype"]}</td>
                <td className="px-4 py-3 text-xs">{row["Modalities Analysed"]}</td>
                <td className="max-w-xs px-4 py-3 text-xs">{row["Core Predictions / Metrics"]}</td>
                <td className="max-w-xs px-4 py-3 text-xs">{row["Enterprise / Comms Fit"]}</td>
                <td className="max-w-sm px-4 py-3 text-xs text-muted-foreground">
                  {row["Signature strength / signal"]}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-8">
        <h2 className="font-display text-sm font-semibold">Backlog coverage summary</h2>
        <p className="text-xs text-muted-foreground">{backlogStories.length} stories tracked in UI</p>
        <div className="mt-2 flex gap-2">
          {(["Done", "Partial", "To Do"] as const).map((s) => (
            <BacklogStatusBadge key={s} status={s} />
          ))}
        </div>
      </div>
    </div>
  );
}
