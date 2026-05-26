from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bt_api_py.bt_api as bt_api_module
from bt_api_base.plugins.loader import PluginLoader
from bt_api_base.registry import ExchangeRegistry
from bt_api_py.bt_api import BtApi


@dataclass
class _FakeEntryPoint:
    name: str = "tradier"
    module: str = "bt_api_tradier.plugin"

    def load(self) -> Any:
        from bt_api_tradier.plugin import register_plugin

        return register_plugin


def setup_function() -> None:
    ExchangeRegistry.clear()
    bt_api_module._runtime_registrar._adapters.clear()


def teardown_function() -> None:
    ExchangeRegistry.clear()
    bt_api_module._runtime_registrar._adapters.clear()


def _load_tradier_plugin(monkeypatch) -> PluginLoader:
    loader = PluginLoader(ExchangeRegistry, bt_api_module._runtime_registrar)
    monkeypatch.setattr(loader, "_discover_entry_points", lambda group: [_FakeEntryPoint()])
    loader.load_all()
    return loader


def test_plugin_loader_registers_bt_api_tradier_for_bt_api(monkeypatch) -> None:
    loader = _load_tradier_plugin(monkeypatch)

    assert "bt_api_tradier" in loader.loaded
    assert bt_api_module._runtime_registrar.get_adapter("TRADIER") is not None
    assert ExchangeRegistry.get_feed_class("TRADIER___STK") is not None
    assert ExchangeRegistry.get_exchange_data_class("TRADIER___STK") is not None

    feed = ExchangeRegistry.create_feed("TRADIER___STK", None, account_id="tradier-paper")
    balance_data = feed.get_balance()
    balance_data.init_data()
    accounts = balance_data.get_data()

    assert len(accounts) == 1
    assert accounts[0].get_account_id() == "tradier-paper"


def test_bt_api_consumes_tradier_plugin_balance_and_subscribe(monkeypatch) -> None:
    _load_tradier_plugin(monkeypatch)

    api = BtApi({"TRADIER___STK": {"account_id": "tradier-paper"}}, debug=False)
    try:
        api.update_total_balance()

        assert api.get_cash("TRADIER___STK", "USD") == 100000.0
        assert api.get_value("TRADIER___STK", "USD") == 50000.0

        api.subscribe(
            "TRADIER___STK___AAPL",
            [{"topic": "kline", "symbol": "AAPL", "period": "1D", "count": 2}],
        )
        data_queue = api.get_data_queue("TRADIER___STK")

        assert data_queue is not None
        first = data_queue.get_nowait()
        second = data_queue.get_nowait()
        assert first["symbol"] == "AAPL"
        assert second["symbol"] == "AAPL"
    finally:
        api.close()
