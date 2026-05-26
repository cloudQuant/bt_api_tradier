from __future__ import annotations

from bt_api_base.balance_utils import simple_balance_handler
from bt_api_base.registry import ExchangeRegistry

from bt_api_tradier.exchange_data import TradierExchangeDataStock
from bt_api_tradier.runtime.feed import TradierRequestDataStock


def _tradier_subscribe_handler(data_queue, exchange_params, topics, bt_api):
    kwargs = dict(exchange_params.items()) if hasattr(exchange_params, "items") else dict(exchange_params or {})
    feed = TradierRequestDataStock(data_queue, **kwargs)
    for topic in topics:
        topic_name = str(topic.get("topic") or "").strip().lower()
        symbol = str(topic.get("symbol") or "").strip().upper()
        if topic_name in {"ticker", "market_data"} and symbol:
            data_queue.put(feed.get_tick(symbol))
        elif topic_name == "kline" and symbol:
            period = str(topic.get("period") or "1D")
            count = int(topic.get("count") or 1)
            bars = feed.get_kline(symbol, period, count=count)
            bars.init_data()
            for row in bars.get_data():
                data_queue.put(row)


def register_tradier(registry: ExchangeRegistry) -> None:
    registry.register_feed("TRADIER___STK", TradierRequestDataStock)
    registry.register_exchange_data("TRADIER___STK", TradierExchangeDataStock)
    registry.register_balance_handler("TRADIER___STK", simple_balance_handler)
    registry.register_stream("TRADIER___STK", "subscribe", _tradier_subscribe_handler)
