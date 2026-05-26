from __future__ import annotations

import time
import uuid
from typing import Any, Optional, Union

from bt_api_base.gateway.adapters.base import BaseGatewayAdapter
from bt_api_base.gateway.models import GatewayTick
from bt_api_base.gateway.protocol import CHANNEL_EVENT, CHANNEL_MARKET

from bt_api_tradier.auth import build_auth_headers, resolve_base_url, validate_credentials
from bt_api_tradier.mapping import (
    environment_account_id,
    map_balance_payload,
    map_order_payload,
    map_position_payload,
    map_quote_payload,
)
from bt_api_tradier.transport import TradierTransportConfig, build_request_context

PositionScalar = Union[float, str]
OrderScalar = Union[float, str, None]


class TradierGatewayAdapter(BaseGatewayAdapter):
    def __init__(self, **kwargs: Any) -> None:
        normalized = dict(kwargs)
        self.paper = bool(normalized.get("paper", True))
        normalized.setdefault("base_url", resolve_base_url(self.paper))
        super().__init__(**normalized)
        self.kwargs = normalized
        self.paper = bool(normalized.get("paper", True))
        self.access_token = str(normalized.get("access_token") or "")
        self.base_url = str(normalized.get("base_url") or resolve_base_url(self.paper))
        self.transport = TradierTransportConfig(
            base_url=self.base_url,
            timeout_sec=float(normalized.get("timeout_sec") or 10.0),
        )
        self.auth_headers = (
            build_auth_headers(access_token=self.access_token) if self.access_token else {}
        )
        self.account_id = str(normalized.get("account_id") or environment_account_id(self.paper))
        self.connected = False
        self.subscribed_symbols: list[str] = []
        self.quotes: dict[str, float] = {"AAPL": 189.25, "MSFT": 425.0}
        self.balance_payload: dict[str, float] = {
            "cash": 50000.0,
            "equity": 50000.0,
            "buying_power": 100000.0,
        }
        self.positions_payload: dict[str, dict[str, PositionScalar]] = {}
        self.orders_payload: dict[str, dict[str, OrderScalar]] = {}
        self.last_request_context: Optional[dict[str, object]] = None

    def connect(self) -> None:
        if self.connected:
            return
        if self.access_token:
            validate_credentials(access_token=self.access_token)
        self.connected = True
        self.emit(
            CHANNEL_EVENT,
            {"kind": "system", "exchange": "TRADIER", "status": "connected", "paper": self.paper},
        )

    def disconnect(self) -> None:
        if not self.connected:
            return
        self.connected = False
        self.emit(CHANNEL_EVENT, {"kind": "system", "exchange": "TRADIER", "status": "disconnected"})

    def subscribe_symbols(self, symbols: list[str]) -> dict[str, Any]:
        done: list[str] = []
        now = time.time()
        for raw_symbol in symbols:
            symbol = str(raw_symbol or "").strip().upper()
            if not symbol:
                continue
            if symbol not in self.subscribed_symbols:
                self.subscribed_symbols.append(symbol)
            done.append(symbol)
            price = self.quotes.get(symbol, 100.0)
            self.emit(
                CHANNEL_MARKET,
                GatewayTick(
                    timestamp=now,
                    local_time=now,
                    symbol=symbol,
                    exchange="TRADIER",
                    asset_type="stk",
                    price=price,
                    bid_price=price - 0.01,
                    ask_price=price + 0.01,
                    instrument_id=symbol,
                    exchange_id="TRADIER",
                ),
            )
        return {"symbols": done}

    def get_balance(self) -> dict[str, Any]:
        self.last_request_context = build_request_context(
            method="GET",
            path=f"/accounts/{self.account_id}/balances",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return map_balance_payload(self.balance_payload)

    def get_positions(self) -> list[dict[str, Any]]:
        return [map_position_payload(payload) for payload in self.positions_payload.values()]

    def place_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        symbol = str(payload.get("symbol") or payload.get("data_name") or "").strip().upper()
        side = str(payload.get("side") or "buy").lower()
        quantity = float(payload.get("volume") or payload.get("size") or 0.0)
        price = float(payload.get("price") or self.quotes.get(symbol, 100.0))
        order_id = str(payload.get("client_order_id") or uuid.uuid4().hex)
        self.last_request_context = build_request_context(
            method="POST",
            path=f"/accounts/{self.account_id}/orders",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        order = map_order_payload(
            {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "status": "filled",
                "price": price,
            }
        )
        self.orders_payload[order_id] = order
        signed_qty = quantity if side == "buy" else -quantity
        position = self.positions_payload.get(symbol)
        if position is None:
            self.positions_payload[symbol] = {
                "symbol": symbol,
                "quantity": signed_qty,
                "cost_basis": price,
                "market_value": signed_qty * price,
            }
        else:
            new_qty = float(position.get("quantity", 0.0)) + signed_qty
            position["quantity"] = new_qty
            position["cost_basis"] = price
            position["market_value"] = new_qty * price
        cash_delta = -(quantity * price) if side == "buy" else quantity * price
        self.balance_payload["cash"] += cash_delta
        self.balance_payload["equity"] = self.balance_payload["cash"]
        self.balance_payload["buying_power"] = self.balance_payload["cash"] * 2
        return order

    def cancel_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        order_id = str(payload.get("order_id") or payload.get("external_order_id") or "")
        existing = self.orders_payload.get(order_id)
        if existing is None:
            cancelled = map_order_payload({"order_id": order_id or "unknown", "status": "canceled"})
            return cancelled
        updated = dict(existing)
        updated["status"] = "canceled"
        self.orders_payload[order_id] = updated
        self.last_request_context = build_request_context(
            method="DELETE",
            path=f"/accounts/{self.account_id}/orders/{order_id}",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return updated

    def get_open_orders(self) -> list[dict[str, Any]]:
        return [
            dict(order)
            for order in self.orders_payload.values()
            if str(order.get("status") or "").lower() not in {"canceled", "filled"}
        ]

    def get_symbol_info(self, symbol: str) -> dict[str, Any]:
        normalized = str(symbol or "").strip().upper()
        return {
            "symbol": normalized,
            "exchange": "TRADIER",
            "asset_type": "STK",
        }

    def get_bars(self, symbol: str, timeframe: str, count: int) -> list[dict[str, Any]]:
        normalized = str(symbol or "").strip().upper()
        price = self.quotes.get(normalized, 100.0)
        now = int(time.time())
        return [
            {
                "timestamp": float(now - index * 60),
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": 0.0,
                "symbol": normalized,
                "timeframe": timeframe,
            }
            for index in range(max(count, 0))
        ]

    def get_quote(self, symbol: str) -> dict[str, object]:
        normalized = str(symbol or "").strip().upper()
        return map_quote_payload(normalized, {"price": self.quotes.get(normalized, 100.0)}, provider="tradier")
