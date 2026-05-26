from __future__ import annotations

import time
from typing import Any

from bt_api_base.containers.accounts.account import AccountData


class TradierAccountData(AccountData):
    def __init__(
        self,
        account_info: Any,
        symbol_name: str | None = None,
        asset_type: str = "STK",
        has_been_json_encoded: bool = True,
    ) -> None:
        super().__init__(account_info, has_been_json_encoded)
        self.exchange_name = "TRADIER"
        self.symbol_name = symbol_name
        self.asset_type = asset_type
        self.local_update_time = time.time()
        self.account_data = account_info if has_been_json_encoded else None
        self.has_been_init_data = False

    def init_data(self):
        if self.has_been_init_data:
            return self
        info = self.account_info if isinstance(self.account_info, dict) else {}
        self.account_id = str(info.get("account_id") or "")
        self.account_type = str(info.get("currency") or "USD")
        self.total_margin = float(info.get("equity", info.get("value", 0.0)) or 0.0)
        self.total_available_margin = float(info.get("buying_power", info.get("cash", 0.0)) or 0.0)
        self.total_unrealized_profit = float(info.get("unrealized_pnl", 0.0) or 0.0)
        self.total_wallet_balance = self.total_margin
        self.has_been_init_data = True
        return self

    def get_exchange_name(self):
        return self.exchange_name

    def get_symbol_name(self):
        return self.symbol_name

    def get_asset_type(self):
        return self.asset_type

    def get_server_time(self):
        return self.server_time

    def get_local_update_time(self):
        return self.local_update_time

    def get_account_id(self):
        return self.account_id

    def get_account_type(self):
        return self.account_type

    def get_can_deposit(self):
        return None

    def get_can_trade(self):
        return None

    def get_can_withdraw(self):
        return None

    def get_fee_tier(self):
        return None

    def get_max_withdraw_amount(self):
        return None

    def get_margin(self):
        return self.total_margin

    def get_total_margin(self):
        return self.total_margin

    def get_used_margin(self):
        return None

    def get_total_used_margin(self):
        return None

    def get_maintain_margin(self):
        return None

    def get_total_maintain_margin(self):
        return None

    def get_available_margin(self):
        return self.total_available_margin

    def get_total_available_margin(self):
        return self.total_available_margin

    def get_open_order_initial_margin(self):
        return None

    def get_total_open_order_initial_margin(self):
        return None

    def get_open_order_maintenance_margin(self):
        return None

    def get_total_position_initial_margin(self):
        return None

    def get_unrealized_profit(self):
        return self.total_unrealized_profit

    def get_total_unrealized_profit(self):
        return self.total_unrealized_profit

    def get_total_wallet_balance(self):
        return self.total_wallet_balance

    def get_balances(self):
        return [self]

    def get_positions(self):
        return []

    def get_spot_maker_commission_rate(self):
        return None

    def get_spot_taker_commission_rate(self):
        return None

    def get_future_maker_commission_rate(self):
        return None

    def get_future_taker_commission_rate(self):
        return None

    def get_option_maker_commission_rate(self):
        return None

    def get_option_taker_commission_rate(self):
        return None

    def get_all_data(self):
        self.init_data()
        return {
            "exchange_name": self.exchange_name,
            "account_id": self.account_id,
            "account_type": self.account_type,
            "asset_type": self.asset_type,
            "total_margin": self.total_margin,
            "total_available_margin": self.total_available_margin,
            "total_unrealized_profit": self.total_unrealized_profit,
            "total_wallet_balance": self.total_wallet_balance,
        }

    def __str__(self):
        return str(self.get_all_data())

    def __repr__(self):
        return self.__str__()
