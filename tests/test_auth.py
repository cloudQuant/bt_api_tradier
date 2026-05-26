import pytest

from bt_api_tradier.auth import (
    LIVE_BASE_URL,
    SANDBOX_BASE_URL,
    build_auth_headers,
    resolve_base_url,
    validate_credentials,
)


def test_resolve_base_url_for_paper_and_live() -> None:
    assert resolve_base_url(True) == SANDBOX_BASE_URL
    assert resolve_base_url(False) == LIVE_BASE_URL


def test_build_auth_headers_uses_bearer_token() -> None:
    headers = build_auth_headers(access_token="demo-token")

    assert headers["Authorization"] == "Bearer demo-token"
    assert headers["Accept"] == "application/json"


@pytest.mark.parametrize("access_token", ["",])
def test_validate_credentials_rejects_missing_values(access_token: str) -> None:
    with pytest.raises(ValueError):
        validate_credentials(access_token=access_token)
