"""Tests for ControllableAdapter verification behavior."""

from __future__ import annotations

import pytest

from gridenforcer_adapter import (
    AdapterData,
    AdapterType,
    ControllableAdapter,
    DeviceClass,
    PowerCapabilities,
    PowerCommandResult,
    VerificationResult,
)


class _FakeControllable(ControllableAdapter):
    """Minimal concrete ControllableAdapter for testing the verify hook."""

    def __init__(self, actual_power_kw: float | None, tolerance: float = 0.5) -> None:
        super().__init__(hass=None, entry_id="test", config={})
        self._actual = actual_power_kw
        self.verification_tolerance_kw = tolerance

    @property
    def adapter_type(self) -> AdapterType:
        return AdapterType.STORAGE

    @property
    def device_class(self) -> DeviceClass:
        return DeviceClass.HOME_BATTERY

    @property
    def name(self) -> str:
        return "fake_controllable"

    @property
    def power_capabilities(self) -> PowerCapabilities:
        return PowerCapabilities(
            rated_min_charge_kw=0.0,
            rated_max_charge_kw=10.0,
            actual_power_kw=self._actual if self._actual is not None else 0.0,
            supports_discharge=True,
            rated_min_discharge_kw=0.0,
            rated_max_discharge_kw=10.0,
        )

    async def async_update(self) -> AdapterData:
        return AdapterData(value=self._actual, unit="kW")

    async def async_set_power(
        self, power_kw: float, *, force: bool = False
    ) -> PowerCommandResult:
        self._actual = power_kw
        return PowerCommandResult(
            success=True,
            requested_power_kw=power_kw,
            actual_power_kw=power_kw,
            executed_at=__import__("datetime").datetime.now(),
        )


class _NoDataControllable(_FakeControllable):
    @property
    def power_capabilities(self) -> PowerCapabilities | None:  # type: ignore[override]
        return None


def test_verification_defaults():
    """Defaults match the plan: 10 s delay, 0.5 kW tolerance, 3 failures."""
    a = _FakeControllable(actual_power_kw=0.0)
    assert a.verification_delay_seconds == 10.0
    assert a.verification_tolerance_kw == 0.5
    assert a.verification_max_failures == 3


async def test_verified_within_tolerance():
    a = _FakeControllable(actual_power_kw=3.3, tolerance=0.5)
    result = await a.async_verify_last_command(3.0)
    assert isinstance(result, VerificationResult)
    assert result.state == "verified"
    assert result.requested_power_kw == 3.0
    assert result.actual_power_kw == 3.3
    assert result.delta_kw == pytest.approx(0.3, abs=1e-9)


async def test_mismatch_outside_tolerance():
    a = _FakeControllable(actual_power_kw=0.0, tolerance=0.5)
    result = await a.async_verify_last_command(3.0)
    assert result.state == "mismatch"
    assert result.delta_kw == pytest.approx(3.0, abs=1e-9)


async def test_tolerance_boundary_inclusive():
    """delta == tolerance counts as verified (<=)."""
    a = _FakeControllable(actual_power_kw=2.5, tolerance=0.5)
    result = await a.async_verify_last_command(3.0)
    assert result.state == "verified"


async def test_no_data_when_capabilities_missing():
    a = _NoDataControllable(actual_power_kw=None)
    result = await a.async_verify_last_command(5.0)
    assert result.state == "no_data"
    assert result.actual_power_kw is None
    assert result.delta_kw is None


async def test_override_can_short_circuit():
    """Subclasses can override with protocol-specific logic."""

    class _Plugged(_FakeControllable):
        plug_status = "unplugged"

        async def async_verify_last_command(self, requested_power_kw):
            if self.plug_status != "plugged":
                return VerificationResult(
                    state="not_applicable",
                    requested_power_kw=requested_power_kw,
                    actual_power_kw=None,
                    delta_kw=None,
                    checked_at=__import__("datetime").datetime.now(),
                    detail="plug_status=unplugged",
                )
            return await super().async_verify_last_command(requested_power_kw)

    a = _Plugged(actual_power_kw=0.0)
    result = await a.async_verify_last_command(3.0)
    assert result.state == "not_applicable"
    assert result.detail == "plug_status=unplugged"
