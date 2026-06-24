"use client";

import { useRouter } from "next/navigation";

import { RoleBadge } from "@/components/role-badge";
import type { SessionUser } from "@/lib/auth";
import { logout } from "@/lib/auth";

export function UserMenu({ user }: { user: SessionUser }) {
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.push("/login");
    router.refresh();
  }

  return (
    <div className="flex items-center gap-3">
      <div className="hidden text-right sm:block">
        <p className="text-sm font-medium text-neutral-900">{user.email}</p>
        <div className="mt-0.5 flex flex-wrap justify-end gap-1">
          {user.role_labels.map((label) => (
            <RoleBadge key={label} label={label} />
          ))}
        </div>
      </div>
      <button
        type="button"
        onClick={handleLogout}
        className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
      >
        Sign out
      </button>
    </div>
  );
}
