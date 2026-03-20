"""Base adapter interface for input sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class AdapterType(Enum):
    """Types of input adapters."""

    GRID_PRICE = "grid_price"
    PRODUCTION = "production"
    CONSUMPTION = "consumption"
    STORAGE = "storage"
    METER = "meter"
    WEATHER = "weather"
    AGGREGATE = "aggregate"
    DEFERRABLE = "deferrable"
    CUSTOM = "custom"


class DeviceClass(Enum):
    """Device class for adapters — refines adapter_type.

    Allows downstream code (UI entities, planning engines) to
    distinguish between e.g. a home battery and an EV charger,
    both of which are STORAGE adapters.
    """

    HOME_BATTERY = "home_battery"
    EV_CHARGER = "ev_charger"
    SOLAR_INVERTER = "solar_inverter"
    GRID_METER = "grid_meter"
    LOAD_METER = "load_meter"
    HEAT_PUMP = "heat_pump"
    GENERIC = "generic"


class ValueType(Enum):
    """Typed tags for measurements an adapter reports."""

    # Power (instantaneous, kW)
    POWER = "power"
    GRID_POWER = "grid_power"
    GRID_IMPORT_POWER = "grid_import_power"
    GRID_EXPORT_POWER = "grid_export_power"
    LOAD_POWER = "load_power"
    BATTERY_POWER = "battery_power"
    CHARGE_POWER = "charge_power"
    DISCHARGE_POWER = "discharge_power"
    # Energy (cumulative, kWh)
    ENERGY_IMPORT = "energy_import"
    ENERGY_EXPORT = "energy_export"
    CAPACITY = "capacity"
    # State (dimensionless)
    SOC = "soc"
    # Price
    ENERGY_PRICE = "energy_price"
    # Forecast (time series)
    POWER_FORECAST = "power_forecast"
    PRICE_FORECAST = "price_forecast"
    # Limits (rated/configured, kW)
    MAX_CHARGE_POWER = "max_charge_power"
    MAX_DISCHARGE_POWER = "max_discharge_power"


class AdapterStatus(Enum):
    """Adapter status states."""

    INITIALIZING = "initializing"
    READY = "ready"
    UPDATING = "updating"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AdapterData:
    """Data returned by an adapter."""

    value: float | int | str | dict[str, Any]
    unit: str | None
    timestamp: datetime
    attributes: dict[str, Any] | None = None
    values: dict[ValueType, float | list[Any] | None] | None = None


class BaseAdapter(ABC):
    """Abstract base class for input adapters."""

    def __init__(
        self,
        hass,
        entry_id: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize adapter."""
        self.hass = hass
        self.entry_id = entry_id
        self.config = config
        self._status = AdapterStatus.INITIALIZING
        self._last_error: str | None = None
        self._parent_id: str | None = None
        self._child_ids: list[str] = []

    @property
    @abstractmethod
    def adapter_type(self) -> AdapterType:
        """Return the adapter type."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return human-readable adapter name."""

    @property
    def device_class(self) -> DeviceClass:
        """Return device class for this adapter.

        Override in subclasses to provide a more specific class.
        Default is GENERIC.
        """
        return DeviceClass.GENERIC

    @property
    def status(self) -> AdapterStatus:
        """Return current adapter status."""
        return self._status

    @property
    def last_error(self) -> str | None:
        """Return last error message if any."""
        return self._last_error

    @property
    def parent_id(self) -> str | None:
        """Return parent adapter ID if this is a child adapter."""
        return self._parent_id

    @property
    def child_ids(self) -> list[str]:
        """Return list of child adapter IDs."""
        return self._child_ids.copy()

    @property
    def is_parent(self) -> bool:
        """Check if this adapter has children."""
        return len(self._child_ids) > 0

    @property
    def is_child(self) -> bool:
        """Check if this adapter has a parent."""
        return self._parent_id is not None

    def set_parent(self, parent_id: str) -> None:
        """Set parent adapter ID."""
        self._parent_id = parent_id

    def add_child(self, child_id: str) -> None:
        """Add a child adapter ID."""
        if child_id not in self._child_ids:
            self._child_ids.append(child_id)

    def remove_child(self, child_id: str) -> None:
        """Remove a child adapter ID."""
        if child_id in self._child_ids:
            self._child_ids.remove(child_id)

    def get_hierarchy_info(self) -> dict[str, Any]:
        """Get hierarchy information."""
        return {
            "parent_id": self._parent_id,
            "child_ids": self._child_ids.copy(),
            "is_parent": self.is_parent,
            "is_child": self.is_child,
        }

    @abstractmethod
    async def async_update(self) -> AdapterData:
        """Fetch latest data from the source.

        Returns:
            AdapterData with current value

        Raises:
            AdapterError: If update fails
        """

    async def async_setup(self) -> bool:
        """Set up the adapter.

        Called once during initialization.
        Override to perform setup tasks.

        Returns:
            True if setup succeeded, False otherwise
        """
        self._status = AdapterStatus.READY
        return True

    async def async_teardown(self) -> None:  # noqa: B027
        """Clean up adapter resources.

        Called when integration is unloaded.
        Override to perform cleanup.
        """

    def validate_config(self) -> bool:
        """Validate adapter configuration.

        Override to add specific validation.

        Returns:
            True if config is valid
        """
        return True
