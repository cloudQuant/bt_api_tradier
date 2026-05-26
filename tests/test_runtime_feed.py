from bt_api_base.balance_utils import simple_balance_handler

from bt_api_tradier.runtime.feed import TradierRequestDataStock


def test_runtime_feed_balance_returns_request_data_with_account_container() -> None:
    feed = TradierRequestDataStock(account_id="tradier-paper")

    balance_data = feed.get_balance()
    balance_data.init_data()
    accounts = balance_data.get_data()
    value_result, cash_result = simple_balance_handler(accounts)

    assert len(accounts) == 1
    assert accounts[0].get_account_id() == "tradier-paper"
    assert value_result["USD"]["value"] == 50000.0
    assert cash_result["USD"]["cash"] == 100000.0


def test_runtime_feed_kline_make_order_and_cancel_order_have_minimal_behavior() -> None:
    feed = TradierRequestDataStock(account_id="tradier-paper")

    bars = feed.get_kline("AAPL", "1D", count=3)
    order = feed.make_order("AAPL", 2, 189.25, "limit")
    cancelled = feed.cancel_order("AAPL", order["order_id"])

    bars.init_data()
    rows = bars.get_data()

    assert len(rows) == 3
    assert rows[0]["symbol"] == "AAPL"
    assert order["symbol"] == "AAPL"
    assert order["status"] == "filled"
    assert cancelled["status"] == "canceled"
