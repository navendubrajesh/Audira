"""Direct social OAuth — users authenticate straight with each provider.

No third-party auth broker. Each provider does the standard OAuth 2.0 /
OpenID Connect authorization-code flow; we exchange the code server-side and
issue our own Audira session JWT.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx
import jwt

from app.config import settings

SUPPORTED_PROVIDERS = ("google", "github", "linkedin", "apple")

PROVIDER_LABELS: dict[str, str] = {
    "google": "Google",
    "github": "GitHub",
    "linkedin": "LinkedIn",
    "apple": "Apple",
}


@dataclass(frozen=True)
class ProviderConfig:
    id: str
    authorize_url: str
    token_url: str
    scope: str
    userinfo_url: str | None = None
    response_mode: str | None = None  # apple uses "form_post"


PROVIDERS: dict[str, ProviderConfig] = {
    "google": ProviderConfig(
        id="google",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
        scope="openid email profile",
    ),
    "github": ProviderConfig(
        id="github",
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scope="read:user user:email",
    ),
    "linkedin": ProviderConfig(
        id="linkedin",
        authorize_url="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken",
        userinfo_url="https://api.linkedin.com/v2/userinfo",
        scope="openid profile email",
    ),
    "apple": ProviderConfig(
        id="apple",
        authorize_url="https://appleid.apple.com/auth/authorize",
        token_url="https://appleid.apple.com/auth/token",
        scope="name email",
        response_mode="form_post",
    ),
}


class OAuthError(Exception):
    """Raised when an OAuth exchange or profile lookup fails."""


def _credentials(provider: str) -> tuple[str, str]:
    mapping = {
        "google": (settings.google_client_id, settings.google_client_secret),
        "github": (settings.github_client_id, settings.github_client_secret),
        "linkedin": (settings.linkedin_client_id, settings.linkedin_client_secret),
        "apple": (settings.apple_client_id, _apple_client_secret()),
    }
    return mapping.get(provider, ("", ""))


def is_provider_configured(provider: str) -> bool:
    if provider == "apple":
        return bool(
            settings.apple_client_id
            and settings.apple_team_id
            and settings.apple_key_id
            and settings.apple_private_key
        )
    client_id, client_secret = _credentials(provider)
    return bool(client_id and client_secret)


def configured_providers() -> list[dict[str, str]]:
    return [
        {"id": p, "label": PROVIDER_LABELS[p]}
        for p in SUPPORTED_PROVIDERS
        if is_provider_configured(p)
    ]


def _apple_client_secret() -> str:
    """Generate the short-lived ES256 client secret Apple requires."""
    if not (
        settings.apple_client_id
        and settings.apple_team_id
        and settings.apple_key_id
        and settings.apple_private_key
    ):
        return ""
    try:
        now = datetime.now(UTC)
        payload = {
            "iss": settings.apple_team_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=30)).timestamp()),
            "aud": "https://appleid.apple.com",
            "sub": settings.apple_client_id,
        }
        return jwt.encode(
            payload,
            settings.apple_private_key,
            algorithm="ES256",
            headers={"kid": settings.apple_key_id},
        )
    except Exception:  # missing cryptography / malformed key
        return ""


def build_authorize_url(provider: str, state: str) -> str:
    from urllib.parse import urlencode

    config = PROVIDERS[provider]
    client_id, _ = _credentials(provider)
    params = {
        "client_id": client_id,
        "redirect_uri": settings.oauth_redirect_uri,
        "response_type": "code",
        "scope": config.scope,
        "state": state,
    }
    if config.response_mode:
        params["response_mode"] = config.response_mode
    if provider == "google":
        params["access_type"] = "online"
        params["prompt"] = "select_account"
    return f"{config.authorize_url}?{urlencode(params)}"


async def _exchange_code(provider: str, code: str) -> dict:
    config = PROVIDERS[provider]
    client_id, client_secret = _credentials(provider)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.oauth_redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            config.token_url,
            data=data,
            headers={"Accept": "application/json"},
        )
    if response.status_code >= 400:
        raise OAuthError(f"{provider} token exchange failed: {response.text}")
    return response.json()


async def _profile_from_google(token: dict) -> tuple[str, str]:
    access_token = token.get("access_token")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            PROVIDERS["google"].userinfo_url,  # type: ignore[arg-type]
            headers={"Authorization": f"Bearer {access_token}"},
        )
    resp.raise_for_status()
    info = resp.json()
    email = info.get("email")
    sub = info.get("sub") or email
    if not email:
        raise OAuthError("Google account has no email")
    return email, str(sub)


async def _profile_from_github(token: dict) -> tuple[str, str]:
    access_token = token.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        user_resp.raise_for_status()
        user = user_resp.json()
        email = user.get("email")
        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails", headers=headers
            )
            emails_resp.raise_for_status()
            emails = emails_resp.json()
            primary = next(
                (e for e in emails if e.get("primary") and e.get("verified")),
                next((e for e in emails if e.get("verified")), None),
            )
            email = primary.get("email") if primary else None
    if not email:
        raise OAuthError("GitHub account has no verified email")
    return email, str(user.get("id"))


async def _profile_from_linkedin(token: dict) -> tuple[str, str]:
    access_token = token.get("access_token")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            PROVIDERS["linkedin"].userinfo_url,  # type: ignore[arg-type]
            headers={"Authorization": f"Bearer {access_token}"},
        )
    resp.raise_for_status()
    info = resp.json()
    email = info.get("email")
    sub = info.get("sub") or email
    if not email:
        raise OAuthError("LinkedIn account has no email")
    return email, str(sub)


def _profile_from_apple(token: dict) -> tuple[str, str]:
    id_token = token.get("id_token")
    if not id_token:
        raise OAuthError("Apple returned no id_token")
    # Trusted: obtained directly from Apple over TLS using our client secret.
    claims = jwt.decode(id_token, options={"verify_signature": False})
    email = claims.get("email")
    sub = claims.get("sub")
    if not email or not sub:
        raise OAuthError("Apple id_token missing email/sub")
    return email, str(sub)


async def complete_login(provider: str, code: str) -> tuple[str, str]:
    """Exchange the authorization code and return (email, provider_user_id)."""
    token = await _exchange_code(provider, code)
    if provider == "google":
        return await _profile_from_google(token)
    if provider == "github":
        return await _profile_from_github(token)
    if provider == "linkedin":
        return await _profile_from_linkedin(token)
    if provider == "apple":
        return _profile_from_apple(token)
    raise OAuthError(f"Unsupported provider: {provider}")


def sign_state(provider: str, return_url: str) -> str:
    payload = {
        "provider": provider,
        "return_url": return_url,
        "exp": int((datetime.now(UTC) + timedelta(minutes=15)).timestamp()),
        "iss": "audira-oauth",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_state(state: str) -> tuple[str, str]:
    data = jwt.decode(
        state, settings.jwt_secret, algorithms=["HS256"], issuer="audira-oauth"
    )
    return data["provider"], data.get("return_url") or settings.web_app_url
