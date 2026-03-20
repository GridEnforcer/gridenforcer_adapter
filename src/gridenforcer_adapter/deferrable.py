"""Deferrable Load adapter for GridEnforcer.

Represents a shiftable load (washing machine, dishwasher, EV charger, etc.)
that EMHASS can schedule to run during cheap-price windows.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .base import AdapterData, AdapterStatus, AdapterType, BaseAdapter

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


def _strip_seconds(t: str | None) -> str | None:
    """Normalize time string to HH:MM, dropping seconds if present."""
    if not t:
        return None
    return ":".join(t.split(":")[:2])


def _optional_float(config: dict, key: str) -> float | None:
    """Return float from config if present and non-None, else None."""
    val = config.get(key)
    return float(val) if val is not None else None


class DeferrableLoadAdapter(BaseAdapter):
    """Adapter for a shiftable load EMHASS can schedule."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the deferrable load adapter."""
        super().__init__(hass, entry_id, config)
        self._entity_id: str | None = config.get("entity_id") or None
        self._name: str = str(config.get("name", "Deferrable Load"))
        self._nominal_power_w: float = float(config["nominal_power_w"])
        self._operating_hours: float = float(config["operating_hours"])
        self._start_time: str | None = _strip_seconds(config.get("start_time"))
        self._end_time: str | None = _strip_seconds(config.get("end_time"))
        self._is_constant: bool = bool(config.get("is_constant", True))
        self._startup_penalty: float = float(config.get("startup_penalty", 0.0))
        # Condition fields
        self._start_condition_entity: str | None = (
            config.get("start_condition_entity") or None
        )
        self._start_condition_above: float | None = _optional_float(
            config, "start_condition_above"
        )
        self._start_condition_below: float | None = _optional_float(
            config, "start_condition_below"
        )
        self._end_condition_entity: str | None = (
            config.get("end_condition_entity") or None
        )
        self._end_condition_above: float | None = _optional_float(
            config, "end_condition_above"
        )
        self._end_condition_below: float | None = _optional_float(
            config, "end_condition_below"
        )
        # When set, the execution engine calls async_set_power() on this adapter
        # instead of turning the entity_id on/off.
        self._controllable_adapter_id: str | None = (
            config.get("controllable_adapter_id") or None
        )

    @property
    def adapter_type(self) -> AdapterType:
        """Return the adapter type."""
        return AdapterType.DEFERRABLE

    @property
    def name(self) -> str:
        """Return human-readable adapter name."""
        return self._name

    @property
    def controllable_adapter_id(self) -> str | None:
        """Return the linked ControllableAdapter ID, or None for entity-based loads."""
        return self._controllable_adapter_id

    def to_planning_dict(self) -> dict[str, Any]:
        """Return base planning fields — start/end timesteps computed by coordinator."""
        return {
            "nominal_power_w": self._nominal_power_w,
            "operating_hours": self._operating_hours,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "is_semi_cont": True,
            "is_constant": self._is_constant,
            "startup_penalty": self._startup_penalty,
        }

    def _evaluate_condition(
        self,
        entity_id: str | None,
        above: float | None,
        below: float | None,
    ) -> bool:
        """Return True if the condition is met or not configured."""
        if not entity_id:
            return True
        state = self.hass.states.get(entity_id)
        if not state or state.state in ("unavailable", "unknown"):
            return False
        try:
            lookup = {"on": 1.0, "off": 0.0, "true": 1.0, "false": 0.0}
            key = state.state.lower()
            val = lookup[key] if key in lookup else float(state.state)
        except (ValueError, AttributeError):
            return False
        if above is not None and val < above:
            return False
        if below is not None and val > below:
            return False
        return True

    @property
    def is_start_condition_met(self) -> bool:
        """Return True if start condition is satisfied (or not configured)."""
        return self._evaluate_condition(
            self._start_condition_entity,
            self._start_condition_above,
            self._start_condition_below,
        )

    @property
    def is_end_condition_met(self) -> bool:
        """Return True if end condition is satisfied (or not configured)."""
        return self._evaluate_condition(
            self._end_condition_entity,
            self._end_condition_above,
            self._end_condition_below,
        )

    @property
    def has_end_condition(self) -> bool:
        """Return True if an end condition entity is configured."""
        return self._end_condition_entity is not None

    async def async_setup(self) -> bool:
        """Set up the adapter."""
        self._status = AdapterStatus.READY
        _LOGGER.info(
            "Deferrable load adapter initialized: name=%s, power=%.0f W, hours=%.2f h",
            self._name,
            self._nominal_power_w,
            self._operating_hours,
        )
        return True

    async def async_update(self) -> AdapterData:
        """Fetch current load state."""
        value: float = 0.0
        if self._entity_id:
            state = self.hass.states.get(self._entity_id)
            if state and state.state not in ("unavailable", "unknown"):
                value = 1.0 if state.state in ("on", "running", "active") else 0.0

        return AdapterData(
            value=value,
            unit=None,
            timestamp=datetime.now(timezone.utc),
            attributes={
                "nominal_power_w": self._nominal_power_w,
                "operating_hours": self._operating_hours,
                "monitored_entity": self._entity_id,
                "start_condition_met": self.is_start_condition_met,
                "end_condition_met": self.is_end_condition_met,
            },
        )
