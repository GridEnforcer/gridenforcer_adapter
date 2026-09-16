# Changelog

## Unreleased

## 0.3.0

Gives a near-zero hold an explicit direction, so a caller at a SoC floor can say which side to hold on instead of encoding it as a magnitude that collides with an adapter's own minimum-power constant (gridenforcer_core ge-7yhs).

- Add `hold_side: HoldSide | None` keyword-only argument to `ControllableAdapter.async_set_power()`, and export the new `HoldSide = Literal["charge", "discharge"]` type. A near-zero target is a *hold*, and a hold was direction-less at this interface: the caller passes one signed number, so an adapter that keeps a session alive with a small trickle had to infer the side from its own session history. That inference is wrong at a SoC floor, where the last real command was a discharge but holding on the discharge side drains the pack further. Callers now state the side instead of encoding it as a magnitude — gridenforcer_core previously had to send +0.1 kW purely because that was the smallest value the InfyPower adapter would still route down its charge path, which tied the two repos' constants together (`FLOOR_HOLD_CHARGE_KW == MIN_POWER_KW == 0.1`) and silently disabled that adapter's keep-alive pulse. Default is `None`, which leaves the choice to the adapter and is correct for every device whose hold has no direction. Refs ge-7yhs, ge-cgon.

## 0.2.0

First tagged release. Pins the protocol contract so downstream repos can depend on a stable tag instead of `main` (gridenforcer_core ge-awz).

- **`BaseAdapter.async_set_grid_export_limit_kw(limit_kw: float) -> bool`.** New default-no-op method on the base contract. Adapters that surface an inverter / EMS knob capping the plant's runtime grid out-flow (e.g. Sigen's `number.sigen_plant_grid_export_limitation`) override this and write the value; adapters without the capability return `False` and the caller treats that as "this adapter can't honor the cap" and moves on. Used by gridenforcer_core-xcm as a runtime safety net to clamp grid export to 0 when the live sell price is ≤ 0 — EMHASS already plans correctly around negative prices (floors `prod_price_forecast` at 0, models PV curtailment as an LP slack), so this is purely a defensive check against reality drift. New test in `tests/test_base.py` pins the default-no-op contract.

- Add `BaseAdapter.is_forecast_only` property (default `False`) so adapters wrapping forecast sensors can opt out of live-state aggregation while still publishing planning attributes
- Add `intent: IntentType | None` keyword-only argument to `ControllableAdapter.async_set_power()` so adapters can branch on the planner's strategic intent (`SELF_CONSUME`, `GRID_CHARGE`, `HOLD`, …) instead of inferring direction from the kW sign — e.g. picking a hybrid-inverter mode that differs between self-consume and grid-charge at identical kW, or republishing the intent on a status sensor. Default is `None` for adapters that don't care; `async_stop()` forwards `IntentType.HOLD`.
- Add `IntentType` enum (`HOLD`, `SELF_CONSUME`, `SELF_DISCHARGE`, `GRID_CHARGE`, `GRID_DISCHARGE`) plus `GRID_DEADBAND_KW` / `BATTERY_DEADBAND_KW` constants for shared use between planning and execution
- Add `force: bool = False` kwarg to `ControllableAdapter.async_set_power` so callers can request a bypass of adapter-level session-state preflight checks
- Add VerificationResult + `async_verify_last_command` default on ControllableAdapter for deferred post-command power checks
- Add PRD.md and update Definition of Done in CLAUDE.md
- Add DeferrableLoadAdapter, DEFERRABLE type, and HEAT_PUMP device class
- Add typed values (ValueType enum) to AdapterData
- Add METER adapter type with GRID_METER and LOAD_METER device classes
- Add AggregateConstraintAdapter base class
- Initial adapter base classes (BaseAdapter, ControllableAdapter, AdapterType, DeviceClass)
