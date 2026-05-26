from bt_api_tradier.gateway.adapter import TradierGatewayAdapter


def test_gateway_adapter_connect_balance_and_positions() -> None:
    adapter = TradierGatewayAdapter(access_token="demo-token", paper=True)

    adapter.connect()
    balance = adapter.get_balance()
    positions = adapter.get_positions()
    adapter.disconnect()

    assert balance["cash"] == 50000.0
    assert balance["value"] == 50000.0
    assert balance["buying_power"] == 100000.0
    assert positions == []


def test_gateway_adapter_subscribe_place_and_cancel_order() -> None:
    adapter = TradierGatewayAdapter(access_token="demo-token", paper=True)

    subscribed = adapter.subscribe_symbols(["AAPL"])
    order = adapter.place_order({"symbol": "AAPL", "side": "buy", "volume": 2, "price": 189.25})
    cancelled = adapter.cancel_order({"order_id": order["order_id"]})

    assert subscribed == {"symbols": ["AAPL"]}
    assert order["symbol"] == "AAPL"
    assert order["status"] == "filled"
    assert cancelled["order_id"] == order["order_id"]
