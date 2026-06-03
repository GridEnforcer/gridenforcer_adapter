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
from typing import Literal

from .base import AdapterStatus, BaseAdapter
from .intent import IntentType

VerificationState = Literal["verified", "mismatch", "no_data", "not_applicable"]


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


@dataclass
class VerificationResult:
    """Outcome of a deferred check that a prior power command took effect."""

    state: VerificationState
    requested_power_kw: float
    actual_power_kw: float | None
    delta_kw: float | None
    checked_at: datetime
    detail: str | None = None


class ControllableAdapter(BaseAdapter):
    """Base class for adapters that can receive power control commands.

    Extends BaseAdapter with methods for setting power output/input.
    Used for devices like EV chargers, batteries, and other controllable loads.
    """

    # Verification tunables — override in subclasses for slow or noisy devices.
    verification_delay_seconds: float = 10.0
    verification_tolerance_kw: float = 0.5
    verification_max_failures: int = 3

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
    async def async_set_power(
        self,
        power_kw: float,
        *,
        force: bool = False,
        intent: IntentType | None = None,
    ) -> PowerCommandResult:
        """Set the target power for this device.

        Positive values indicate charging/consumption.
        Negative values indicate discharging/production (if supported).

        Args:
            power_kw: Target power in kW
            force: If True, bypass adapter-level defensive preflight checks
                (e.g. session-state guards) because the caller has explicit
                user intent and accepts responsibility for the outcome.
                Hardware-availability checks still apply.
            intent: The planner's strategic intent for this command (e.g.
                ``SELF_CONSUME``, ``GRID_CHARGE``, ``HOLD``). Adapters may
                use this to choose protocol-specific behavior — for
                example, a hybrid inverter could pick a different mode for
                ``SELF_CONSUME`` vs ``GRID_CHARGE`` even when the kW
                target is identical, or expose the intent on a status
                sensor for downstream automations. Adapters that don't
                care can ignore it.

        Returns:
            PowerCommandResult indicating success/failure and actual power set
        """

    async def async_stop(self) -> PowerCommandResult:
        """Stop power flow (set power to 0).

        Returns:
            PowerCommandResult indicating success/failure
        """
        return await self.async_set_power(0.0, intent=IntentType.HOLD)

    async def async_verify_last_command(
        self, requested_power_kw: float
    ) -> VerificationResult:
        """Check whether the last commanded power has been reached.

        Called by the execution engine after `verification_delay_seconds` has
        elapsed since a successful `async_set_power`. The default compares
        `power_capabilities.actual_power_kw` against the request with
        `verification_tolerance_kw`; subclasses may override for
        protocol-specific checks (e.g. also inspecting session state).

        Args:
            requested_power_kw: The power that was most recently commanded.

        Returns:
            VerificationResult describing the outcome.
        """
        caps = self.power_capabilities
        actual = caps.actual_power_kw if caps is not None else None
        checked_at = datetime.now()
        if actual is None:
            return VerificationResult(
                state="no_data",
                requested_power_kw=requested_power_kw,
                actual_power_kw=None,
                delta_kw=None,
                checked_at=checked_at,
            )
        delta = abs(actual - requested_power_kw)
        state: VerificationState = (
            "verified" if delta <= self.verification_tolerance_kw else "mismatch"
        )
        return VerificationResult(
            state=state,
            requested_power_kw=requested_power_kw,
            actual_power_kw=actual,
            delta_kw=delta,
            checked_at=checked_at,
        )

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
