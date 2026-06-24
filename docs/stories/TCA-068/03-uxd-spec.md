# TCA-068 — UXD Spec

## Residency card (settings preview on home, authenticated Security/Admin)

- Card title: "Data residency"
- Two-column layout: Storage region | Processing region
- Badges for encryption (AES-256) and TLS (1.2+)
- Green "Tenant isolation active" indicator

## Hand-off → FSD

Use `ResidencyCard` component; read-only for most roles, edit dropdown for Admin/Security.
