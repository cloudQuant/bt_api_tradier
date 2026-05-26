# bt_api_tradier

Tradier broker plugin package for `bt_api`.

## Install

```bash
pip install -e .
```

## Plugin Entry Point

The package exposes the old plugin mode entry point in `pyproject.toml`:

```toml
[project.entry-points."bt_api.plugins"]
tradier = "bt_api_tradier.plugin:register_plugin"
```

## Usage

```python
from bt_api_tradier.gateway.adapter import TradierGatewayAdapter

adapter = TradierGatewayAdapter(access_token="demo-token", paper=True)
adapter.connect()

balance = adapter.get_balance()
positions = adapter.get_positions()
```

## Testing

```bash
python -m pytest tests/test_auth.py tests/test_mapping.py tests/test_transport.py tests/test_exchange_data.py tests/test_runtime_feed.py tests/test_plugin.py tests/test_contract.py tests/test_bt_api_integration.py -q
```
