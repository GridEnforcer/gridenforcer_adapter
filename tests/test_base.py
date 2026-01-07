"""Tests for base adapter classes."""

from datetime import datetime

import pytest

from gridenforcer_adapter import AdapterData, AdapterStatus, AdapterType, BaseAdapter


def test_adapter_type_enum():
    """Test that AdapterType enum has expected values."""
    assert AdapterType.GRID_PRICE.value == "grid_price"
    assert AdapterType.PRODUCTION.value == "production"
    assert AdapterType.CONSUMPTION.value == "consumption"
    assert AdapterType.STORAGE.value == "storage"
    assert AdapterType.WEATHER.value == "weather"
    assert AdapterType.CUSTOM.value == "custom"


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
