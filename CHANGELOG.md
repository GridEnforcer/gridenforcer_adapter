# Changelog

## Unreleased

- Add `IntentType` enum (`HOLD`, `SELF_CONSUME`, `SELF_DISCHARGE`, `GRID_CHARGE`, `GRID_DISCHARGE`) plus `GRID_DEADBAND_KW` / `BATTERY_DEADBAND_KW` constants for shared use between planning and execution
- Add `force: bool = False` kwarg to `ControllableAdapter.async_set_power` so callers can request a bypass of adapter-level session-state preflight checks
- Add VerificationResult + `async_verify_last_command` default on ControllableAdapter for deferred post-command power checks
- Add PRD.md and update Definition of Done in CLAUDE.md
- Add DeferrableLoadAdapter, DEFERRABLE type, and HEAT_PUMP device class
- Add typed values (ValueType enum) to AdapterData
- Add METER adapter type with GRID_METER and LOAD_METER device classes
- Add AggregateConstraintAdapter base class
- Initial adapter base classes (BaseAdapter, ControllableAdapter, AdapterType, DeviceClass)
