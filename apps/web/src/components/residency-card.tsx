"use client";

import { useEffect, useState } from "react";

import { getApiUrl, getSessionToken } from "@/lib/auth";

type Residency = {
  storage_region_label: string;
  processing_region_label: string;
  encryption_at_rest: string;
  tls_min_version: string;
  tenant_isolation: boolean;
};

export function ResidencyCard() {
  const [data, setData] = useState<Residency | null>(null);

  useEffect(() => {
    const token = getSessionToken();
    if (!token) return;
    fetch(`${getApiUrl()}/tenant/residency`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) return null;

  return (
    <section className="mt-8 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-neutral-900">Data residency</h2>
      <p className="mt-1 text-sm text-neutral-500">
        Your data is stored and processed in {data.storage_region_label}.
      </p>
      <dl className="mt-4 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium text-neutral-500">Storage region</dt>
          <dd className="text-sm font-medium text-neutral-900">{data.storage_region_label}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-neutral-500">Processing region</dt>
          <dd className="text-sm font-medium text-neutral-900">{data.processing_region_label}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-neutral-500">Encryption at rest</dt>
          <dd className="text-sm text-neutral-900">{data.encryption_at_rest}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-neutral-500">Data in transit</dt>
          <dd className="text-sm text-neutral-900">TLS {data.tls_min_version}+</dd>
        </div>
      </dl>
      {data.tenant_isolation ? (
        <p className="mt-4 text-xs font-medium text-emerald-700">Tenant isolation active</p>
      ) : null}
    </section>
  );
}
