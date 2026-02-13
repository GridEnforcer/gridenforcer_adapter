"""Controllable adapter interface for devices that can receive power commands.

Naming conventions for power values:
- rated_*: Hardware/spec limits (static, what device CAN do)
- ems_*: Current EMS/system limits (dynamic, read from device)
- target_*: Commanded/requested values (what we're asking for)
- actual_*: Real-time measurements (what's actually happening)
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime

from .base import AdapterStatus, BaseAdapter


@dataclass
class PowerCapabilities:
    """Power capabilities of a controllable adapter.

    Uses clear naming convention:
    - rated_*: Hardware/spec limits (static)
    - actual_*: Current measurements (dynamic)
    """

    # Rated/hardware limits for charging (static specs)
    rated_min_charge_kw: float
    rated_max_charge_kw: float

    # Current actual power (real-time measurement)
    actual_power_kw: float

    # Discharge support
    supports_discharge: bool = False
    rated_min_discharge_kw: float = 0.0
    rated_max_discharge_kw: float = 0.0


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
            PowerCapabilities with rated limits and actual state
        """

    @property
    def rated_min_charge_kw(self) -> float:
        """Return rated minimum charge power in kW."""
        return self.power_capabilities.rated_min_charge_kw

    @property
    def rated_max_charge_kw(self) -> float:
        """Return rated maximum charge power in kW."""
        return self.power_capabilities.rated_max_charge_kw

    @property
    def actual_power_kw(self) -> float:
        """Return actual current power in kW."""
        return self.power_capabilities.actual_power_kw

    @property
    def rated_max_discharge_kw(self) -> float:
        """Return rated maximum discharge power in kW."""
        return self.power_capabilities.rated_max_discharge_kw

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
            True if the power level is within rated capabilities
        """
        if self._status != AdapterStatus.READY:
            return False

        caps = self.power_capabilities

        if power_kw >= 0:
            # Charging/consumption
            return caps.rated_min_charge_kw <= power_kw <= caps.rated_max_charge_kw
        else:
            # Discharging/production
            if not caps.supports_discharge:
                return False
            abs_power = abs(power_kw)
            return caps.rated_min_discharge_kw <= abs_power <= caps.rated_max_discharge_kw
