# Changelog

## Unreleased

- **0.1.2 — `BaseAdapter.async_set_grid_export_limit_kw(limit_kw: float) -> bool`.** New default-no-op method on the base contract. Adapters that surface an inverter / EMS knob capping the plant's runtime grid out-flow (e.g. Sigen's `number.sigen_plant_grid_export_limitation`) override this and write the value; adapters without the capability return `False` and the caller treats that as "this adapter can't honor the cap" and moves on. Used by gridenforcer_core-xcm as a runtime safety net to clamp grid export to 0 when the live sell price is ≤ 0 — EMHASS already plans correctly around negative prices (floors `prod_price_forecast` at 0, models PV curtailment as an LP slack), so this is purely a defensive check against reality drift. New test in `tests/test_base.py` pins the default-no-op contract.

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
