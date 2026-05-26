from bt_api_tradier import TradierExchangeDataStock
from bt_api_tradier.exchange_data import TradierExchangeData


def test_exchange_data_stock_exposes_expected_rest_url_and_exchange_name() -> None:
    data = TradierExchangeDataStock()

    assert isinstance(data, TradierExchangeData)
    assert data.exchange_name == "TRADIER"
    assert data.rest_url.startswith("https://")
    assert data.wss_url.startswith("wss://")
