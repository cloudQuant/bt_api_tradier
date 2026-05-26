from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bt_api_base.gateway.registrar import GatewayRuntimeRegistrar
    from bt_api_base.registry import ExchangeRegistry

from bt_api_base.plugins.protocol import PluginInfo

from bt_api_tradier import __version__
from bt_api_tradier.gateway.adapter import TradierGatewayAdapter
from bt_api_tradier.registry_registration import register_tradier


def register_plugin(
    registry: type[ExchangeRegistry], runtime_factory: type[GatewayRuntimeRegistrar]
) -> PluginInfo:
    register_tradier(registry)
    runtime_factory.register_adapter("TRADIER", TradierGatewayAdapter)

    return PluginInfo(
        name="bt_api_tradier",
        version=__version__,
        core_requires=">=0.15,<1.0",
        supported_exchanges=("TRADIER___STK",),
        supported_asset_types=("STK",),
    )
