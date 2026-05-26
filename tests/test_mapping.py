from bt_api_tradier.mapping import (
    environment_account_id,
    map_balance_payload,
    map_order_payload,
    map_position_payload,
    map_quote_payload,
)


def test_environment_account_id_uses_paper_and_live_names() -> None:
    assert environment_account_id(True) == "tradier-paper"
    assert environment_account_id(False) == "tradier-live"


def test_map_quote_payload_returns_stable_quote_shape() -> None:
    quote = map_quote_payload("AAPL", {"price": 189.25}, provider="tradier")

    assert quote == {
        "symbol": "AAPL",
        "price": 189.25,
        "provider": "tradier",
    }


def test_map_balance_payload_returns_gateway_balance_shape() -> None:
    account = map_balance_payload(
        {
            "cash": 10000.0,
            "equity": 10250.0,
            "buying_power": 19800.0,
        }
    )

    assert account["cash"] == 10000.0
    assert account["value"] == 10250.0
    assert account["buying_power"] == 19800.0


def test_map_order_payload_returns_gateway_order_shape() -> None:
    order = map_order_payload(
        {
            "order_id": "ord-1",
            "symbol": "AAPL",
            "side": "buy",
            "quantity": 2.0,
            "status": "filled",
        }
    )

    assert order["order_id"] == "ord-1"
    assert order["symbol"] == "AAPL"
    assert order["status"] == "filled"
    assert order["quantity"] == 2.0


def test_map_position_payload_returns_gateway_position_shape() -> None:
    position = map_position_payload(
        {
            "symbol": "AAPL",
            "quantity": 3,
            "cost_basis": 188.5,
            "market_value": 567.0,
        }
    )

    assert position["instrument"] == "AAPL"
    assert position["volume"] == 3.0
    assert position["price"] == 188.5
    assert position["market_value"] == 567.0
