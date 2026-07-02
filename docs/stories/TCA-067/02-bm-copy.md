# TCA-067 — BM Copy

## Product strings

| Key | Copy |
|---|---|
| `login.title` | Sign in to Audira.run |
| `login.subtitle` | Enterprise SSO for your organisation |
| `login.button` | Continue with SSO |
| `login.dev_notice` | Development mode — use configured test credentials |
| `logout.button` | Sign out |
| `session.welcome` | Signed in as {email} |
| `roles.label` | Your roles |

## Role display names

| Role ID | Label |
|---|---|
| `owner` | Owner |
| `admin` | Administrator |
| `comms_manager` | Comms Manager |
| `internal_comms_lead` | Internal Comms Lead |
| `exec_office_writer` | Exec-Office Writer |
| `ld_lead` | L&D Lead |
| `policy_compliance` | Policy / Compliance Officer |
| `brand_manager` | Brand Manager |
| `reviewer` | Reviewer |
| `ml_platform_eng` | ML / Platform Engineer |
| `security` | Security / IT |

## Error messages

| Key | Copy |
|---|---|
| `auth.denied.title` | Access not authorised |
| `auth.denied.body` | Your account does not have permission to view this resource. Contact your administrator if you believe this is an error. |
| `auth.session_expired` | Your session has expired. Please sign in again. |
| `auth.sso_error` | We could not complete sign-in. Please try again or contact your IT administrator. |

## Audit log labels

| Action | Label |
|---|---|
| `auth.login` | Signed in |
| `auth.logout` | Signed out |
| `auth.access_denied` | Access denied |
| `scim.user_provisioned` | User provisioned (SCIM) |
| `scim.user_updated` | User updated (SCIM) |
| `scim.user_deprovisioned` | User deprovisioned (SCIM) |

## Compliance note (UI footer on login)

Audira.run uses your organisation's identity provider. We do not store your SSO password. Access is logged for security and compliance purposes.

## Hand-off → UXD

Login is a single primary CTA; role badge on header after auth; access-denied is a full-page empathetic state with link back to home.
