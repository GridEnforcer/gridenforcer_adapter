"""Controllable adapter interface for devices that can receive power commands."""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime

from .base import AdapterStatus, BaseAdapter


@dataclass
class PowerCapabilities:
    """Power capabilities of a controllable adapter."""

    min_power_kw: float
    max_power_kw: float
    current_power_kw: float
    supports_discharge: bool = False
    min_discharge_power_kw: float = 0.0
    max_discharge_power_kw: float = 0.0


@dataclass
class PowerCommandResult:
    """Result of a power command execution."""

    success: bool
    requested_power_kw: float
    actual_power_kw: float | None
    executed_at: datetime
    error_message: str | None = None


class ControllableAdapter(BaseAdapter):
    """Base class for adapters that can receive power control commands.

    Extends BaseAdapter with methods for setting power output/input.
    Used for devices like EV chargers, batteries, and other controllable loads.
    """

    @property
    def is_controllable(self) -> bool:
        """Return True as this adapter supports control commands."""
        return True

    @property
    @abstractmethod
    def power_capabilities(self) -> PowerCapabilities:
        """Return current power capabilities.

        Returns:
            PowerCapabilities with min/max power limits and current state
        """

    @property
    def min_power_kw(self) -> float:
        """Return minimum power in kW (convenience property)."""
        return self.power_capabilities.min_power_kw

    @property
    def max_power_kw(self) -> float:
        """Return maximum power in kW (convenience property)."""
        return self.power_capabilities.max_power_kw

    @property
    def current_power_kw(self) -> float:
        """Return current power in kW (convenience property)."""
        return self.power_capabilities.current_power_kw

    @abstractmethod
    async def async_set_power(self, power_kw: float) -> PowerCommandResult:
        """Set the target power for this device.

        Positive values indicate charging/consumption.
        Negative values indicate discharging/production (if supported).

        Args:
            power_kw: Target power in kW

        Returns:
            PowerCommandResult indicating success/failure and actual power set
        """

    async def async_stop(self) -> PowerCommandResult:
        """Stop power flow (set power to 0).

        Returns:
            PowerCommandResult indicating success/failure
        """
        return await self.async_set_power(0.0)

    def can_accept_power(self, power_kw: float) -> bool:
        """Check if the device can accept the requested power level.

        Args:
            power_kw: Requested power in kW

        Returns:
            True if the power level is within capabilities
        """
        if self._status != AdapterStatus.READY:
            return False

        caps = self.power_capabilities

        if power_kw >= 0:
            # Charging/consumption
            return caps.min_power_kw <= power_kw <= caps.max_power_kw
        else:
            # Discharging/production
            if not caps.supports_discharge:
                return False
            abs_power = abs(power_kw)
            return caps.min_discharge_power_kw <= abs_power <= caps.max_discharge_power_kw
