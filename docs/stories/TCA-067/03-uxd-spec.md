# TCA-067 — UXD Spec

## Screens

### 1. Login (`/login`)

- Centred card on neutral-50 background
- Audira.run logo + product name
- H1: "Sign in to Audira.run"
- Subtitle: "Enterprise SSO for your organisation"
- Primary button (brand-600): "Continue with SSO" → `{API}/auth/login`
- Footer compliance note (12px neutral-500)
- WCAG: focus ring on button; contrast ≥ 4.5:1

### 2. Auth callback (`/auth/callback`)

- Loading spinner + "Completing sign-in…"
- Reads `token` query param from API redirect
- Stores session in cookie (`audira_session`)
- Redirects to `/`

### 3. App shell (authenticated)

- Header: logo | user email + role badges | Sign out
- Unauthenticated visitors to `/` see login CTA

### 4. Access denied (`/access-denied`)

- Icon + title + body from BM copy
- Secondary link: "Return to home"

## Components

- `LoginCard` — login page
- `UserMenu` — email + roles + logout
- `RoleBadge` — pill per role (brand-50 bg)

## Interaction

- Sign out → POST `/auth/logout` + clear cookie → `/login`
- Session missing on protected view → redirect `/login?returnUrl=…`

## Hand-off → FSD

Use design tokens; no custom colours outside `@audira/design-tokens`.
