"""WorkOS SSO client wrapper."""

from typing import Literal
from urllib.parse import urlencode

import httpx

from app.config import settings

WORKOS_AUTH_URL = "https://api.workos.com/user_management/authorize"
WORKOS_TOKEN_URL = "https://api.workos.com/user_management/authenticate"

OAuthProvider = Literal[
    "authkit",
    "GoogleOAuth",
    "AppleOAuth",
    "GitHubOAuth",
    "LinkedInOAuth",
]

OAUTH_PROVIDERS: frozenset[str] = frozenset(
    {"GoogleOAuth", "AppleOAuth", "GitHubOAuth", "LinkedInOAuth"}
)


def is_workos_configured() -> bool:
    return bool(settings.workos_api_key and settings.workos_client_id)


def get_authorization_url(
    state: str | None = None,
    provider: OAuthProvider = "authkit",
) -> str:
    params = {
        "client_id": settings.workos_client_id,
        "redirect_uri": settings.workos_redirect_uri,
        "response_type": "code",
        "provider": provider,
    }
    if state:
        params["state"] = state
    return f"{WORKOS_AUTH_URL}?{urlencode(params)}"


async def authenticate_with_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            WORKOS_TOKEN_URL,
            headers={"Authorization": f"Bearer {settings.workos_api_key}"},
            json={
                "client_id": settings.workos_client_id,
                "client_secret": settings.workos_api_key,
                "grant_type": "authorization_code",
                "code": code,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
