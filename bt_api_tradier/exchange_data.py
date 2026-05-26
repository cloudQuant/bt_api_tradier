from __future__ import annotations

from bt_api_base.containers.exchanges.exchange_data import ExchangeData

from bt_api_tradier.auth import LIVE_BASE_URL, SANDBOX_BASE_URL

SANDBOX_WSS_URL = "wss://ws.tradier.com/v1/markets/events"
LIVE_WSS_URL = "wss://ws.tradier.com/v1/markets/events"

__all__ = ["TradierExchangeData", "TradierExchangeDataStock"]


class TradierExchangeData(ExchangeData):
    def __init__(self, asset_type: str = "STK", paper: bool = True) -> None:
        super().__init__()
        self.exchange_name = "TRADIER"
        self.asset_type = asset_type
        self.rest_url = SANDBOX_BASE_URL if paper else LIVE_BASE_URL
        self.wss_url = SANDBOX_WSS_URL if paper else LIVE_WSS_URL
        self.acct_wss_url = self.wss_url
        self.rest_paths = {
            "get_account": "/user/profile",
            "get_balances": "/accounts/{account_id}/balances",
            "get_positions": "/accounts/{account_id}/positions",
            "get_orders": "/accounts/{account_id}/orders",
            "get_quote": "/markets/quotes",
            "get_history": "/markets/history",
        }
        self.kline_periods = {
            "1Min": "minute",
            "1D": "daily",
            "1W": "weekly",
        }
        self.reverse_kline_periods = {value: key for key, value in self.kline_periods.items()}
        self.legal_currency = ["USD"]

    def get_rest_path(self, key: str) -> str:
        path = self.rest_paths.get(key)
        if not path:
            self.raise_path_error(self.exchange_name, key)
        return str(path)

    def get_rest_url(self, key: str, **params: str) -> tuple[str, str]:
        path = self.get_rest_path(key).format(**params)
        return "GET", f"{self.rest_url}{path}"


class TradierExchangeDataStock(TradierExchangeData):
    def __init__(self) -> None:
        super().__init__(asset_type="STK", paper=True)
