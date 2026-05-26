from bt_api_tradier.transport import TradierTransportConfig, build_request_context


def test_transport_config_uses_timeout_and_base_url() -> None:
    config = TradierTransportConfig(base_url="https://sandbox.tradier.com/v1", timeout_sec=12.5)

    assert config.base_url == "https://sandbox.tradier.com/v1"
    assert config.timeout_sec == 12.5


def test_build_request_context_combines_method_path_headers_and_timeout() -> None:
    context = build_request_context(
        method="GET",
        path="/accounts/tradier-paper/balances",
        headers={"Authorization": "Bearer demo"},
        timeout_sec=8.0,
    )

    assert context["method"] == "GET"
    assert context["path"] == "/accounts/tradier-paper/balances"
    assert context["headers"]["Authorization"] == "Bearer demo"
    assert context["timeout_sec"] == 8.0
