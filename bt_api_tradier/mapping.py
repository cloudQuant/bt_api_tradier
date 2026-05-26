from __future__ import annotations

from typing import Union

Scalar = Union[float, str]
OrderScalar = Union[float, str, None]


def environment_account_id(paper: bool) -> str:
    return "tradier-paper" if paper else "tradier-live"


def map_balance_payload(payload: dict[str, Scalar]) -> dict[str, float]:
    cash = float(payload.get("cash", payload.get("total_cash", 0.0)))
    value = float(payload.get("equity", payload.get("value", cash)))
    buying_power = float(payload.get("buying_power", payload.get("available_cash", cash)))
    return {
        "cash": cash,
        "value": value,
        "buying_power": buying_power,
    }


def map_order_payload(payload: dict[str, Scalar]) -> dict[str, OrderScalar]:
    order_id = str(payload.get("order_id", payload.get("id", "order-unknown")))
    return {
        "id": order_id,
        "order_id": order_id,
        "external_order_id": str(payload.get("external_order_id", order_id)),
        "symbol": str(payload.get("symbol", "UNKNOWN")),
        "side": str(payload.get("side", "buy")),
        "quantity": float(payload.get("quantity", 0.0)),
        "status": str(payload.get("status", "new")),
        "price": float(payload["price"]) if "price" in payload else None,
    }


def map_position_payload(payload: dict[str, Scalar]) -> dict[str, Scalar]:
    return {
        "instrument": str(payload.get("symbol", "UNKNOWN")),
        "volume": float(payload.get("quantity", payload.get("qty", 0.0))),
        "price": float(payload.get("cost_basis", payload.get("avg_entry_price", 0.0))),
        "market_value": float(payload.get("market_value", 0.0)),
    }


def map_quote_payload(symbol: str, payload: dict[str, float], *, provider: str) -> dict[str, object]:
    return {
        "symbol": symbol,
        "price": float(payload.get("price", 0.0)),
        "provider": provider,
    }
