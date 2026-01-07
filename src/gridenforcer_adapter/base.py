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
    WEATHER = "weather"
    CUSTOM = "custom"


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

    @property
    @abstractmethod
    def adapter_type(self) -> AdapterType:
        """Return the adapter type."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return human-readable adapter name."""

    @property
    def status(self) -> AdapterStatus:
        """Return current adapter status."""
        return self._status

    @property
    def last_error(self) -> str | None:
        """Return last error message if any."""
        return self._last_error

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

    async def async_teardown(self) -> None:
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
