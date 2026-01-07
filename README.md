# GridEnforcer Adapter

Shared adapter base classes for Home Assistant energy management integrations.

## Overview

This package provides a common interface for data source adapters used in Home Assistant energy management integrations. It defines abstract base classes that allow different integrations to share a consistent pattern for accessing:

- Grid electricity prices
- Solar/wind production data
- Household consumption metrics
- Battery storage state
- Weather forecasts
- Custom data sources

## Installation

### As a Git Dependency (Current)

Add to your Home Assistant integration's `manifest.json`:

```json
{
  "requirements": [
    "gridenforcer-adapter @ git+https://github.com/GridEnforcer/gridenforcer_adapter.git@main"
  ]
}
```

### From PyPI (Coming Soon)

```bash
pip install gridenforcer-adapter
```

## Usage

### Creating a Custom Adapter

```python
from datetime import datetime
from gridenforcer_adapter import BaseAdapter, AdapterData, AdapterType

class MyPriceAdapter(BaseAdapter):
    """Adapter for fetching electricity prices."""

    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.GRID_PRICE

    @property
    def name(self) -> str:
        return "My Price Provider"

    async def async_update(self) -> AdapterData:
        """Fetch latest price data."""
        # Fetch from your data source
        price = await self._fetch_current_price()

        return AdapterData(
            value=price,
            unit="EUR/kWh",
            timestamp=datetime.now(),
            attributes={
                "provider": "my_provider",
                "currency": "EUR",
            }
        )

    async def _fetch_current_price(self) -> float:
        """Implement your data fetching logic here."""
        # Example: query an API, read from HA entity, etc.
        entity_id = self.config.get("price_entity_id")
        state = self.hass.states.get(entity_id)
        return float(state.state)
```

### Using the Adapter

```python
# In your Home Assistant integration
from homeassistant.core import HomeAssistant

adapter = MyPriceAdapter(
    hass=hass,
    entry_id="my_integration_entry",
    config={
        "price_entity_id": "sensor.electricity_price"
    }
)

# Setup the adapter
await adapter.async_setup()

# Fetch data
data = await adapter.async_update()
print(f"Current price: {data.value} {data.unit}")
```

## Adapter Types

The package includes predefined adapter types:

- `GRID_PRICE`: Electricity grid prices
- `PRODUCTION`: Energy production (solar, wind, etc.)
- `CONSUMPTION`: Household energy consumption
- `STORAGE`: Battery storage state
- `WEATHER`: Weather forecasts
- `CUSTOM`: Custom data sources

## Adapter Lifecycle

Adapters support a complete lifecycle:

1. **Initialization**: `__init__(hass, entry_id, config)`
2. **Setup**: `async_setup()` - Called once during initialization
3. **Updates**: `async_update()` - Called periodically to fetch data
4. **Teardown**: `async_teardown()` - Called when integration is unloaded

## Adapter Status

Adapters track their status through the `AdapterStatus` enum:

- `INITIALIZING`: Adapter is being set up
- `READY`: Adapter is ready to fetch data
- `UPDATING`: Adapter is currently fetching data
- `ERROR`: Adapter encountered an error
- `DISABLED`: Adapter has been disabled

Access via `adapter.status` property.

## Configuration Validation

Override `validate_config()` to add custom validation:

```python
def validate_config(self) -> bool:
    """Validate that required config keys are present."""
    return all(key in self.config for key in ["entity_id", "min_value", "max_value"])
```

## Example Implementations

See the [GridEnforcer Core](https://github.com/GridEnforcer/gridenforcer_core) integration for complete examples of:

- Battery storage adapter
- Nordpool price adapter
- Production/consumption adapters
- Coordinator pattern for managing multiple adapters

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=gridenforcer_adapter --cov-report=html
```

### Code Quality

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type check
mypy src/
```

## Requirements

- Python >= 3.12
- No runtime dependencies (uses only Python standard library)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

## Links

- [GitHub Repository](https://github.com/GridEnforcer/gridenforcer_adapter)
- [GridEnforcer Core Integration](https://github.com/GridEnforcer/gridenforcer_core)
- [Home Assistant](https://www.home-assistant.io/)
