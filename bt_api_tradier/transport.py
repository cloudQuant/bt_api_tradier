from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradierTransportConfig:
    base_url: str
    timeout_sec: float = 10.0


def build_request_context(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    timeout_sec: float,
) -> dict[str, object]:
    return {
        "method": method,
        "path": path,
        "headers": headers,
        "timeout_sec": timeout_sec,
    }
