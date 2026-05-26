from bt_api_base.plugins.protocol import PluginInfo
from bt_api_base.registry import ExchangeRegistry

from bt_api_tradier import __version__
from bt_api_tradier.exchange_data import TradierExchangeDataStock
from bt_api_tradier.gateway.adapter import TradierGatewayAdapter
from bt_api_tradier.plugin import register_plugin
from bt_api_tradier.runtime.feed import TradierRequestDataStock


class _RuntimeFactory:
    adapters: dict[str, type] = {}

    @classmethod
    def register_adapter(cls, exchange: str, adapter: type) -> None:
        cls.adapters[exchange] = adapter


def test_register_plugin_returns_plugin_info() -> None:
    _RuntimeFactory.adapters = {}
    ExchangeRegistry.clear()

    info = register_plugin(ExchangeRegistry, _RuntimeFactory)

    assert isinstance(info, PluginInfo)
    assert info.name == "bt_api_tradier"
    assert info.version == __version__
    assert info.core_requires == ">=0.15,<1.0"
    assert info.supported_exchanges == ("TRADIER___STK",)
    assert info.supported_asset_types == ("STK",)
    assert _RuntimeFactory.adapters["TRADIER"] is TradierGatewayAdapter
    assert ExchangeRegistry.get_feed_class("TRADIER___STK") is TradierRequestDataStock
    assert ExchangeRegistry.get_exchange_data_class("TRADIER___STK") is TradierExchangeDataStock
    assert ExchangeRegistry.get_balance_handler("TRADIER___STK") is not None
    assert ExchangeRegistry.get_stream_class("TRADIER___STK", "subscribe") is not None
