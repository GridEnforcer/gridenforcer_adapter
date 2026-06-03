# GridEnforcer Adapter

Shared adapter base classes for the GridEnforcer energy management ecosystem.

## Overview

This package defines the common interface that all GridEnforcer device integrations implement. It provides abstract base classes, typed value enums, and data structures that enable GridEnforcer Core to communicate with any energy device through a uniform API.

## Adapter Types

| AdapterType | Description |
|-------------|-------------|
| `GRID_PRICE` | Electricity grid prices and forecasts |
| `PRODUCTION` | Energy production (solar, wind) |
| `METER` | Power metering (grid meter, load meter) |
| `STORAGE` | Battery storage and EV chargers |
| `DEFERRABLE` | Deferrable/shiftable loads (heat pumps, water heaters) |
| `AGGREGATE` | Aggregate constraint adapters (multi-device coordination) |

## Device Classes

| DeviceClass | Used with |
|-------------|-----------|
| `SOLAR_INVERTER` | PV production adapters |
| `HOME_BATTERY` | Stationary battery storage |
| `EV_CHARGER` | EV chargers (including V2G) |
| `GRID_METER` | Grid import/export meters |
| `LOAD_METER` | Household consumption meters |
| `HEAT_PUMP` | Heat pump deferrable loads |
| `GENERIC` | Default for unspecified devices |

## Typed Values

Adapters report data using `ValueType` enum keys in `AdapterData.values`:

```python
from gridenforcer_adapter import ValueType

# Storage adapter example
AdapterData(
    values={
        ValueType.SOC: 75.0,
        ValueType.BATTERY_POWER: -3.5,  # kW, negative = discharging
        ValueType.CAPACITY: 10.0,       # kWh
    },
    ...
)
```

Common value types: `SOC`, `BATTERY_POWER`, `CAPACITY`, `POWER`, `GRID_POWER`, `GRID_IMPORT_POWER`, `GRID_EXPORT_POWER`, `LOAD_POWER`, `ENERGY_PRICE`, `PRICE_FORECAST`.

## Base Classes

### BaseAdapter

Read-only adapter with lifecycle management (`async_setup`, `async_update`, `async_teardown`), status tracking, and typed value reporting.

Adapters that wrap a forecast sensor (PV forecast services, ML load forecasters) should override `is_forecast_only` to return `True`. GridEnforcer Core will then keep them out of live state aggregation while still reading their forecast attributes for planning.

### ControllableAdapter

Extends `BaseAdapter` with `async_set_power(power_kw)` for bidirectional power control and `PowerCapabilities` (rated/EMS limits, current power, SOC).

### DeferrableLoadAdapter

Extends `BaseAdapter` for shiftable loads. Provides `to_planning_dict()` for EMHASS integration with nominal power, duration, and time windows.

### AggregateConstraintAdapter

Parent adapter that coordinates multiple child adapters sharing a common constraint (e.g., shared inverter capacity).

## Installation

```json
{
  "requirements": [
    "gridenforcer-adapter @ git+https://github.com/GridEnforcer/gridenforcer_adapter.git@main"
  ]
}
```

## Usage

```python
from gridenforcer_adapter import BaseAdapter, AdapterData, AdapterType, DeviceClass, ValueType

class MyStorageAdapter(ControllableAdapter):
    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.STORAGE

    @property
    def device_class(self) -> DeviceClass:
        return DeviceClass.HOME_BATTERY

    async def async_update(self) -> AdapterData:
        return AdapterData(
            values={ValueType.SOC: 80.0, ValueType.BATTERY_POWER: 2.0},
            unit="kW",
            timestamp=datetime.now(),
        )

    async def async_set_power(self, power_kw: float) -> None:
        ...
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check src/
mypy src/
```

## Requirements

- Python >= 3.12
- No runtime dependencies

## License

MIT
