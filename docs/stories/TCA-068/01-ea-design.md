# TCA-068 — EA Design

**Story:** Data residency & tenant isolation  
**FR:** FR-E17-2

## AC mapping

| AC | Implementation |
|---|---|
| Region-pinned storage/processing | `Tenant` model: `storage_region`, `processing_region` (IN/EU); routing hints for object storage + GPU tier |
| Per-tenant isolation | All queries scoped by `tenant_id`; `assert_tenant_resource()` blocks cross-tenant access |
| AES-256 at rest | Postgres/R2 encryption documented; `encryption_at_rest` + `encryption_key_id` on tenant |
| TLS 1.2+ in transit | Enforced at platform edge; `tls_min_version` on tenant config |
| Managed keys | `encryption_key_id` references KMS/Vault key ARN |

## API

| Method | Path | Auth |
|---|---|---|
| GET | `/tenant/residency` | Authenticated |
| PATCH | `/tenant/residency` | Admin/Owner/Security |
| GET | `/admin/residency/verify` | Security — isolation self-check |

## Hand-off → BM

Region labels, residency summary copy for settings UI.
