import { Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import {
  createAudience,
  deleteAudience,
  listAudiences,
  type Audience,
} from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-001 — Audience & persona library */
export function AudiencesScreen() {
  const [audiences, setAudiences] = useState<Audience[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [role, setRole] = useState("employee");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setAudiences(await listAudiences());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load audiences");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createAudience({ name, role, region: "Global", language: "en", seniority: "all" });
      setName("");
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Create failed");
    }
  }

  if (loading) return <GlobalStatePanel variant="loading" />;
  if (error && !audiences.length) {
    return (
      <GlobalStatePanel variant="error" actionLabel="Retry" onAction={() => void load()} />
    );
  }

  return (
    <PermissionGate permission="audiences.manage">
      <div>
        <div className="mb-4 flex items-center gap-2">
          <h2 className="font-display text-lg font-semibold">Audience library</h2>
          <StoryIdBadge id="TCA-001" />
        </div>
        {error ? <p className="mb-3 text-sm text-danger">{error}</p> : null}

        <form onSubmit={(e) => void handleCreate(e)} className="mb-6 flex flex-wrap gap-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Audience name"
            className="h-9 rounded-lg border border-border px-3 text-sm"
            required
          />
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="Role"
            className="h-9 rounded-lg border border-border px-3 text-sm"
          />
          <Button type="submit" size="sm">
            <Plus className="h-4 w-4" />
            Add audience
          </Button>
        </form>

        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-overlay text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Region</th>
                <th className="px-4 py-3">Default</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {audiences.map((a) => (
                <tr key={a.id} className="border-t border-border">
                  <td className="px-4 py-3 font-medium">{a.name}</td>
                  <td className="px-4 py-3">{a.role}</td>
                  <td className="px-4 py-3">{a.region}</td>
                  <td className="px-4 py-3">{a.is_default ? "Yes" : "—"}</td>
                  <td className="px-4 py-3 text-right">
                    {!a.is_default ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => void deleteAudience(a.id).then(load)}
                        aria-label={`Delete ${a.name}`}
                      >
                        <Trash2 className="h-4 w-4 text-danger" />
                      </Button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PermissionGate>
  );
}
