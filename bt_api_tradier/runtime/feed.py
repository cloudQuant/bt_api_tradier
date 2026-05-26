from __future__ import annotations

import time
import uuid
from typing import Any, Optional, Union

from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.feeds.capability import Capability
from bt_api_base.feeds.feed import Feed

from bt_api_tradier.auth import build_auth_headers, resolve_base_url, validate_credentials
from bt_api_tradier.containers.tradier_account import TradierAccountData
from bt_api_tradier.exchange_data import TradierExchangeDataStock
from bt_api_tradier.mapping import environment_account_id, map_order_payload, map_quote_payload
from bt_api_tradier.transport import TradierTransportConfig, build_request_context

BalanceScalar = Union[float, str]
OrderScalar = Union[float, str, None]


class TradierRequestData(Feed):
    def __init__(self, data_queue: Any = None, **kwargs: Any) -> None:
        normalized = dict(kwargs)
        normalized.setdefault("exchange_name", "TRADIER")
        super().__init__(data_queue, **normalized)
        self.exchange_name = "TRADIER"
        self.asset_type = str(normalized.get("asset_type") or "STK")
        self.paper = bool(normalized.get("paper", True))
        self.base_url = str(normalized.get("base_url") or resolve_base_url(self.paper))
        self.access_token = str(normalized.get("access_token") or "")
        self.account_id = str(normalized.get("account_id") or environment_account_id(self.paper))
        self.transport = TradierTransportConfig(
            base_url=self.base_url,
            timeout_sec=float(normalized.get("timeout_sec") or 10.0),
        )
        self.auth_headers = (
            build_auth_headers(access_token=self.access_token) if self.access_token else {}
        )
        self._params = TradierExchangeDataStock()
        self._params.rest_url = self.base_url
        self.quotes: dict[str, float] = {"AAPL": 189.25, "MSFT": 425.0}
        self.balance_payload: dict[str, BalanceScalar] = {
            "account_id": self.account_id,
            "currency": "USD",
            "cash": 50000.0,
            "equity": 50000.0,
            "buying_power": 100000.0,
            "unrealized_pnl": 0.0,
        }
        self.orders: dict[str, dict[str, OrderScalar]] = {}
        self.last_request_context: Optional[dict[str, object]] = None

    @classmethod
    def _capabilities(cls) -> set[Capability]:
        return {
            Capability.GET_TICK,
            Capability.GET_DEPTH,
            Capability.GET_KLINE,
            Capability.MAKE_ORDER,
            Capability.CANCEL_ORDER,
            Capability.CANCEL_ALL,
            Capability.QUERY_ORDER,
            Capability.QUERY_OPEN_ORDERS,
            Capability.GET_BALANCE,
            Capability.GET_ACCOUNT,
            Capability.GET_POSITION,
        }

    def connect(self) -> None:
        if self.access_token:
            validate_credentials(access_token=self.access_token)
        super().connect()

    def _wrap_request(
        self,
        data: Any,
        *,
        request_type: str,
        symbol_name: Optional[str] = None,
    ) -> RequestData:
        extra_data = {
            "exchange_name": self.exchange_name,
            "symbol_name": symbol_name or "",
            "asset_type": self.asset_type,
            "request_type": request_type,
        }
        return RequestData(data, extra_data)

    def get_tick(self, symbol: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        normalized = str(symbol or "").strip().upper()
        self.last_request_context = build_request_context(
            method="GET",
            path=f"/markets/quotes?symbols={normalized}",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return map_quote_payload(normalized, {"price": self.quotes.get(normalized, 100.0)}, provider="tradier")

    def get_depth(self, symbol: Any, count: int = 5, extra_data: Any = None, **kwargs: Any) -> Any:
        quote = self.get_tick(symbol, extra_data=extra_data, **kwargs)
        price = float(quote.get("price", 0.0))
        return {
            "symbol": quote["symbol"],
            "bids": [[price - 0.01, float(count)]],
            "asks": [[price + 0.01, float(count)]],
            "provider": "tradier",
        }

    def get_kline(
        self,
        symbol: Any,
        period: str,
        count: int = 100,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> RequestData:
        normalized = str(symbol or "").strip().upper()
        price = self.quotes.get(normalized, 100.0)
        now = int(time.time())
        rows = [
            {
                "timestamp": float(now - index * 60),
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": 0.0,
                "symbol": normalized,
                "period": period,
            }
            for index in range(max(count, 0))
        ]
        self.last_request_context = build_request_context(
            method="GET",
            path=f"/markets/history?symbol={normalized}&interval={period}",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return self._wrap_request(rows, request_type="get_kline", symbol_name=normalized)

    def make_order(
        self,
        symbol: Any,
        volume: Any,
        price: Any,
        order_type: str = "limit",
        offset: str = "open",
        post_only: bool = False,
        client_order_id: Optional[str] = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        normalized = str(symbol or "").strip().upper()
        side_value = str(
            kwargs.get("side")
            or (extra_data.get("side") if isinstance(extra_data, dict) else "")
            or order_type
        ).lower()
        side = "sell" if side_value.startswith("sell") else "buy"
        order_id = client_order_id or uuid.uuid4().hex
        mapped = map_order_payload(
            {
                "order_id": order_id,
                "symbol": normalized,
                "side": side,
                "quantity": float(volume),
                "status": "filled",
                "price": float(price or self.quotes.get(normalized, 100.0)),
            }
        )
        self.orders[order_id] = mapped
        self.last_request_context = build_request_context(
            method="POST",
            path=f"/accounts/{self.account_id}/orders",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return mapped

    def cancel_order(self, symbol: Any, order_id: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        key = str(order_id)
        existing = dict(
            self.orders.get(key)
            or map_order_payload({"order_id": key, "symbol": symbol or "", "status": "new"})
        )
        existing["status"] = "canceled"
        self.orders[key] = existing
        self.last_request_context = build_request_context(
            method="DELETE",
            path=f"/accounts/{self.account_id}/orders/{key}",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return existing

    def cancel_all(self, symbol: Any = None, extra_data: Any = None, **kwargs: Any) -> Any:
        return [
            self.cancel_order(symbol, order_id, extra_data=extra_data, **kwargs)
            for order_id in list(self.orders)
        ]

    def query_order(self, symbol: Any, order_id: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        return dict(self.orders.get(str(order_id)) or {})

    def get_open_orders(self, symbol: Any = None, extra_data: Any = None, **kwargs: Any) -> Any:
        return [
            dict(order)
            for order in self.orders.values()
            if str(order.get("status") or "").lower() not in {"canceled", "filled"}
        ]

    def get_position(self, symbol: Any = None, extra_data: Any = None, **kwargs: Any) -> Any:
        return []

    def get_account(self, symbol: Any = None, extra_data: Any = None, **kwargs: Any) -> RequestData:
        account = TradierAccountData(self.balance_payload, symbol_name="USD", asset_type=self.asset_type)
        self.last_request_context = build_request_context(
            method="GET",
            path="/user/profile",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return self._wrap_request([account], request_type="get_account", symbol_name="USD")

    def get_balance(self, symbol: Any = None, extra_data: Any = None, **kwargs: Any) -> RequestData:
        account = TradierAccountData(self.balance_payload, symbol_name="USD", asset_type=self.asset_type)
        self.last_request_context = build_request_context(
            method="GET",
            path=f"/accounts/{self.account_id}/balances",
            headers=dict(self.auth_headers),
            timeout_sec=self.transport.timeout_sec,
        )
        return self._wrap_request([account], request_type="get_balance", symbol_name="USD")


class TradierRequestDataStock(TradierRequestData):
    def __init__(self, data_queue: Any = None, **kwargs: Any) -> None:
        super().__init__(data_queue, **kwargs)
        self.asset_type = str(kwargs.get("asset_type") or "STK")
        self._params = TradierExchangeDataStock()
        self._params.rest_url = self.base_url
