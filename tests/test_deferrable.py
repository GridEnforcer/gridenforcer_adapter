"""Tests for DeferrableLoadAdapter."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from gridenforcer_adapter import AdapterType, DeviceClass, DeferrableLoadAdapter


@pytest.fixture
def hass():
    """Return a mock Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def base_config():
    """Return minimal valid deferrable load config."""
    return {
        "name": "Washing Machine",
        "nominal_power_w": 2000,
        "operating_hours": 2.0,
    }


def test_adapter_type(hass, base_config):
    """DeferrableLoadAdapter reports DEFERRABLE type."""
    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    assert adapter.adapter_type == AdapterType.DEFERRABLE


def test_device_class_default(hass, base_config):
    """DeferrableLoadAdapter defaults to GENERIC device class."""
    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    assert adapter.device_class == DeviceClass.GENERIC


def test_name(hass, base_config):
    """Adapter returns configured name."""
    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    assert adapter.name == "Washing Machine"


def test_to_planning_dict(hass):
    """to_planning_dict returns expected fields."""
    config = {
        "name": "Dishwasher",
        "nominal_power_w": 1800,
        "operating_hours": 1.5,
        "start_time": "08:00:00",
        "end_time": "22:00",
        "is_constant": False,
        "startup_penalty": 0.1,
    }
    adapter = DeferrableLoadAdapter(hass, "entry_1", config)
    d = adapter.to_planning_dict()
    assert d["nominal_power_w"] == 1800
    assert d["operating_hours"] == 1.5
    assert d["start_time"] == "08:00"  # seconds stripped
    assert d["end_time"] == "22:00"
    assert d["is_semi_cont"] is True
    assert d["is_constant"] is False
    assert d["startup_penalty"] == 0.1


def test_controllable_adapter_id(hass, base_config):
    """controllable_adapter_id returns None when not configured."""
    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    assert adapter.controllable_adapter_id is None

    config_with_link = {**base_config, "controllable_adapter_id": "charger_1"}
    adapter2 = DeferrableLoadAdapter(hass, "entry_1", config_with_link)
    assert adapter2.controllable_adapter_id == "charger_1"


def test_start_condition_no_entity(hass, base_config):
    """Start condition is met when no entity configured."""
    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    assert adapter.is_start_condition_met is True


def test_start_condition_above(hass, base_config):
    """Start condition checks above threshold."""
    config = {
        **base_config,
        "start_condition_entity": "sensor.ev_soc",
        "start_condition_above": 20.0,
    }
    adapter = DeferrableLoadAdapter(hass, "entry_1", config)

    # Entity reports 50 — above 20 → met
    state = MagicMock()
    state.state = "50.0"
    hass.states.get.return_value = state
    assert adapter.is_start_condition_met is True

    # Entity reports 10 — below 20 → not met
    state.state = "10.0"
    assert adapter.is_start_condition_met is False


def test_start_condition_boolean_entity(hass, base_config):
    """Start condition handles on/off boolean entities."""
    config = {
        **base_config,
        "start_condition_entity": "binary_sensor.ev_connected",
        "start_condition_above": 0.5,
    }
    adapter = DeferrableLoadAdapter(hass, "entry_1", config)

    state = MagicMock()
    state.state = "on"
    hass.states.get.return_value = state
    assert adapter.is_start_condition_met is True

    state.state = "off"
    assert adapter.is_start_condition_met is False


def test_end_condition(hass, base_config):
    """End condition evaluation works."""
    config = {
        **base_config,
        "end_condition_entity": "sensor.temperature",
        "end_condition_below": 60.0,
    }
    adapter = DeferrableLoadAdapter(hass, "entry_1", config)
    assert adapter.has_end_condition is True

    state = MagicMock()
    state.state = "55.0"
    hass.states.get.return_value = state
    assert adapter.is_end_condition_met is True

    state.state = "65.0"
    assert adapter.is_end_condition_met is False


def test_condition_unavailable_entity(hass, base_config):
    """Condition returns False for unavailable entity."""
    config = {
        **base_config,
        "start_condition_entity": "sensor.missing",
        "start_condition_above": 0.5,
    }
    adapter = DeferrableLoadAdapter(hass, "entry_1", config)

    state = MagicMock()
    state.state = "unavailable"
    hass.states.get.return_value = state
    assert adapter.is_start_condition_met is False

    hass.states.get.return_value = None
    assert adapter.is_start_condition_met is False


@pytest.mark.asyncio
async def test_async_update(hass, base_config):
    """async_update returns AdapterData with correct attributes."""
    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    hass.states.get.return_value = None

    data = await adapter.async_update()
    assert data.value == 0.0
    assert data.attributes["nominal_power_w"] == 2000
    assert data.attributes["operating_hours"] == 2.0


@pytest.mark.asyncio
async def test_async_setup(hass, base_config):
    """async_setup marks adapter as READY."""
    from gridenforcer_adapter import AdapterStatus

    adapter = DeferrableLoadAdapter(hass, "entry_1", base_config)
    result = await adapter.async_setup()
    assert result is True
    assert adapter.status == AdapterStatus.READY
