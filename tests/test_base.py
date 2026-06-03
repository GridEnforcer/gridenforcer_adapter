"""Tests for base adapter classes."""

from datetime import datetime

import pytest

from gridenforcer_adapter import (
    AdapterData,
    AdapterStatus,
    AdapterType,
    BaseAdapter,
    DeviceClass,
    ValueType,
)


def test_adapter_type_enum():
    """Test that AdapterType enum has expected values."""
    assert AdapterType.GRID_PRICE.value == "grid_price"
    assert AdapterType.PRODUCTION.value == "production"
    assert AdapterType.CONSUMPTION.value == "consumption"
    assert AdapterType.STORAGE.value == "storage"
    assert AdapterType.METER.value == "meter"
    assert AdapterType.WEATHER.value == "weather"
    assert AdapterType.CUSTOM.value == "custom"


def test_device_class_enum():
    """Test that DeviceClass enum has expected values."""
    assert DeviceClass.HOME_BATTERY.value == "home_battery"
    assert DeviceClass.EV_CHARGER.value == "ev_charger"
    assert DeviceClass.SOLAR_INVERTER.value == "solar_inverter"
    assert DeviceClass.GRID_METER.value == "grid_meter"
    assert DeviceClass.LOAD_METER.value == "load_meter"
    assert DeviceClass.GENERIC.value == "generic"


def test_value_type_enum():
    """Test that ValueType enum has expected values."""
    # Power
    assert ValueType.POWER.value == "power"
    assert ValueType.GRID_POWER.value == "grid_power"
    assert ValueType.GRID_IMPORT_POWER.value == "grid_import_power"
    assert ValueType.GRID_EXPORT_POWER.value == "grid_export_power"
    assert ValueType.LOAD_POWER.value == "load_power"
    assert ValueType.BATTERY_POWER.value == "battery_power"
    assert ValueType.CHARGE_POWER.value == "charge_power"
    assert ValueType.DISCHARGE_POWER.value == "discharge_power"
    # Energy
    assert ValueType.ENERGY_IMPORT.value == "energy_import"
    assert ValueType.ENERGY_EXPORT.value == "energy_export"
    assert ValueType.CAPACITY.value == "capacity"
    # State
    assert ValueType.SOC.value == "soc"
    # Price
    assert ValueType.ENERGY_PRICE.value == "energy_price"
    # Forecast
    assert ValueType.POWER_FORECAST.value == "power_forecast"
    assert ValueType.PRICE_FORECAST.value == "price_forecast"
    # Limits
    assert ValueType.MAX_CHARGE_POWER.value == "max_charge_power"
    assert ValueType.MAX_DISCHARGE_POWER.value == "max_discharge_power"


def test_adapter_default_device_class():
    """Test that BaseAdapter.device_class defaults to GENERIC."""

    class TestAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.STORAGE

        @property
        def name(self) -> str:
            return "Test"

        async def async_update(self) -> AdapterData:
            return AdapterData(
                value=0, unit=None, timestamp=datetime.now()
            )

    adapter = TestAdapter(
        hass=None, entry_id="test", config={}  # type: ignore
    )
    assert adapter.device_class == DeviceClass.GENERIC


def test_adapter_default_is_forecast_only_false():
    """is_forecast_only defaults to False; live adapters opt out by default."""

    class LiveAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.PRODUCTION

        @property
        def name(self) -> str:
            return "Live PV"

        async def async_update(self) -> AdapterData:
            return AdapterData(value=0, unit=None, timestamp=datetime.now())

    adapter = LiveAdapter(hass=None, entry_id="test", config={})  # type: ignore
    assert adapter.is_forecast_only is False


def test_adapter_is_forecast_only_can_be_overridden():
    """Forecast adapters override is_forecast_only to True."""

    class ForecastAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.PRODUCTION

        @property
        def name(self) -> str:
            return "PV Forecast"

        @property
        def is_forecast_only(self) -> bool:
            return True

        async def async_update(self) -> AdapterData:
            return AdapterData(value=0, unit=None, timestamp=datetime.now())

    adapter = ForecastAdapter(hass=None, entry_id="test", config={})  # type: ignore
    assert adapter.is_forecast_only is True


def test_adapter_custom_device_class():
    """Test that device_class can be overridden."""

    class EVAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.STORAGE

        @property
        def device_class(self) -> DeviceClass:
            return DeviceClass.EV_CHARGER

        @property
        def name(self) -> str:
            return "EV"

        async def async_update(self) -> AdapterData:
            return AdapterData(
                value=0, unit=None, timestamp=datetime.now()
            )

    adapter = EVAdapter(
        hass=None, entry_id="test", config={}  # type: ignore
    )
    assert adapter.device_class == DeviceClass.EV_CHARGER


def test_adapter_status_enum():
    """Test that AdapterStatus enum has expected values."""
    assert AdapterStatus.INITIALIZING.value == "initializing"
    assert AdapterStatus.READY.value == "ready"
    assert AdapterStatus.UPDATING.value == "updating"
    assert AdapterStatus.ERROR.value == "error"
    assert AdapterStatus.DISABLED.value == "disabled"


def test_adapter_data_creation():
    """Test AdapterData dataclass can be instantiated."""
    now = datetime.now()
    data = AdapterData(
        value=42.0,
        unit="kWh",
        timestamp=now,
        attributes={"source": "test"},
    )

    assert data.value == 42.0
    assert data.unit == "kWh"
    assert data.timestamp == now
    assert data.attributes == {"source": "test"}


def test_adapter_data_without_attributes():
    """Test AdapterData can be created without attributes."""
    now = datetime.now()
    data = AdapterData(
        value="active",
        unit=None,
        timestamp=now,
    )

    assert data.value == "active"
    assert data.unit is None
    assert data.attributes is None
    assert data.values is None


def test_adapter_data_with_values():
    """Test AdapterData with typed values dict."""
    now = datetime.now()
    data = AdapterData(
        value=5.0,
        unit="kW",
        timestamp=now,
        values={
            ValueType.GRID_POWER: 5.0,
            ValueType.GRID_IMPORT_POWER: 5.0,
            ValueType.GRID_EXPORT_POWER: 0.0,
        },
    )

    assert data.values is not None
    assert data.values[ValueType.GRID_POWER] == 5.0
    assert data.values[ValueType.GRID_IMPORT_POWER] == 5.0
    assert data.values[ValueType.GRID_EXPORT_POWER] == 0.0


def test_base_adapter_is_abstract():
    """Test that BaseAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseAdapter(hass=None, entry_id="test", config={})  # type: ignore


def test_concrete_adapter_implementation():
    """Test that a concrete adapter can be created."""

    class TestAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.CUSTOM

        @property
        def name(self) -> str:
            return "Test Adapter"

        async def async_update(self) -> AdapterData:
            return AdapterData(
                value=123,
                unit="test",
                timestamp=datetime.now(),
            )

    # Create instance
    adapter = TestAdapter(hass=None, entry_id="test_id", config={"key": "value"})  # type: ignore

    # Test properties
    assert adapter.adapter_type == AdapterType.CUSTOM
    assert adapter.name == "Test Adapter"
    assert adapter.status == AdapterStatus.INITIALIZING
    assert adapter.last_error is None
    assert adapter.config == {"key": "value"}


async def test_concrete_adapter_async_update():
    """Test that async_update works on concrete adapter."""

    class TestAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.PRODUCTION

        @property
        def name(self) -> str:
            return "Test Production"

        async def async_update(self) -> AdapterData:
            return AdapterData(
                value=5000.0,
                unit="W",
                timestamp=datetime.now(),
            )

    adapter = TestAdapter(hass=None, entry_id="test", config={})  # type: ignore
    data = await adapter.async_update()

    assert isinstance(data, AdapterData)
    assert data.value == 5000.0
    assert data.unit == "W"


async def test_adapter_lifecycle_methods():
    """Test adapter setup and teardown methods."""

    class TestAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.CUSTOM

        @property
        def name(self) -> str:
            return "Test"

        async def async_update(self) -> AdapterData:
            return AdapterData(value=0, unit=None, timestamp=datetime.now())

    adapter = TestAdapter(hass=None, entry_id="test", config={})  # type: ignore

    # Initial status is INITIALIZING
    assert adapter.status == AdapterStatus.INITIALIZING

    # Setup should set status to READY
    result = await adapter.async_setup()
    assert result is True
    assert adapter.status == AdapterStatus.READY

    # Teardown should not raise
    await adapter.async_teardown()


@pytest.mark.asyncio
async def test_async_set_grid_export_limit_kw_default_is_no_op():
    """BaseAdapter default returns False so adapters without an inverter
    export-limit knob silently skip the runtime safety-net call.
    gridenforcer_core-xcm."""

    class TestAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.CUSTOM

        @property
        def name(self) -> str:
            return "Test"

        async def async_update(self) -> AdapterData:
            return AdapterData(value=0, unit=None, timestamp=datetime.now())

    adapter = TestAdapter(hass=None, entry_id="test", config={})  # type: ignore
    assert await adapter.async_set_grid_export_limit_kw(0.0) is False
    assert await adapter.async_set_grid_export_limit_kw(10.0) is False


def test_adapter_validate_config():
    """Test config validation method."""

    class TestAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.CUSTOM

        @property
        def name(self) -> str:
            return "Test"

        async def async_update(self) -> AdapterData:
            return AdapterData(value=0, unit=None, timestamp=datetime.now())

        def validate_config(self) -> bool:
            return "required_key" in self.config

    # Valid config
    adapter_valid = TestAdapter(
        hass=None, entry_id="test", config={"required_key": "value"}  # type: ignore
    )
    assert adapter_valid.validate_config() is True

    # Invalid config
    adapter_invalid = TestAdapter(hass=None, entry_id="test", config={})  # type: ignore
    assert adapter_invalid.validate_config() is False
