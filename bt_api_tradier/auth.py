from __future__ import annotations

SANDBOX_BASE_URL = "https://sandbox.tradier.com/v1"
LIVE_BASE_URL = "https://api.tradier.com/v1"


def resolve_base_url(paper: bool) -> str:
    return SANDBOX_BASE_URL if paper else LIVE_BASE_URL


def validate_credentials(*, access_token: str) -> None:
    if not access_token:
        raise ValueError("tradier access_token must not be empty")


def build_auth_headers(*, access_token: str) -> dict[str, str]:
    validate_credentials(access_token=access_token)
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
