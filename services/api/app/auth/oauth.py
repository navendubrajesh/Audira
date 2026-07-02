"""Google OAuth — users sign in directly with their Google account."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
import jwt

from app.config import settings

PROVIDER = "google"
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
SCOPE = "openid email profile"


class OAuthError(Exception):
    """Raised when Google OAuth exchange or profile lookup fails."""


def is_google_configured() -> bool:
    return bool(settings.google_client_id and settings.google_client_secret)


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.oauth_redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def complete_login(code: str) -> tuple[str, str]:
    """Exchange the authorization code and return (email, google_user_id)."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        token_resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.oauth_redirect_uri,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
            },
            headers={"Accept": "application/json"},
        )
        if token_resp.status_code >= 400:
            raise OAuthError(f"Google token exchange failed: {token_resp.text}")

        access_token = token_resp.json().get("access_token")
        if not access_token:
            raise OAuthError("Google returned no access token")

        user_resp = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    user_resp.raise_for_status()
    info = user_resp.json()
    email = info.get("email")
    sub = info.get("sub") or email
    if not email:
        raise OAuthError("Google account has no email")
    return email, str(sub)


def sign_state(return_url: str) -> str:
    payload = {
        "return_url": return_url,
        "exp": int((datetime.now(UTC) + timedelta(minutes=15)).timestamp()),
        "iss": "audira-oauth",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_state(state: str) -> str:
    data = jwt.decode(
        state, settings.jwt_secret, algorithms=["HS256"], issuer="audira-oauth"
    )
    return data.get("return_url") or settings.web_app_url
