# PRD: GridEnforcer Adapter

Shared base classes and type system for all GridEnforcer device adapters — defines the contracts that adapters, the core coordinator, and the execution engine depend on.

## Behavioral Specification

### BaseAdapter Lifecycle

- **When an adapter is instantiated**, status is set to INITIALIZING.
- **When `async_setup()` is called**, status transitions to READY and the adapter can receive `async_update()` calls. Returns True on success, False on failure.
- **When `async_update()` is called**, the adapter fetches current data and returns an AdapterData object with typed values.
- **When `async_teardown()` is called**, the adapter cleans up resources (connections, listeners).
- **When `validate_config()` returns False**, the adapter should not be used (caller decides handling).

### AdapterData

- **When `values` dict is populated** (ValueType keys), the core reads typed measurements directly.
- **When `values` is None**, the core falls back to `value` + `attributes` dict (legacy path).
- **Both paths can coexist** — adapters may populate both for backwards compatibility.

### ControllableAdapter

- **When `async_set_power(power_kw)` is called with positive value**, the device charges at that rate.
- **When called with negative value**, the device discharges (if `supports_discharge` is True).
- **When called with near-zero value** (within adapter threshold), the device stops.
- **When `can_accept_power(power_kw)` is called**, it returns True only if status is READY and the power is within rated capabilities. This is a feasibility check, not a command.
- **When `async_stop()` is called**, it delegates to `async_set_power(0.0)`.

### PowerCapabilities

- **`rated_min/max_charge_kw`**: Hardware limits (static specs).
- **`actual_power_kw`**: Real-time measurement of current power flow.
- **`supports_discharge`**: Whether the device can reverse power flow.
- **`rated_min/max_discharge_kw`**: Discharge limits (only meaningful if `supports_discharge` is True).

### DeferrableLoadAdapter

- **When `to_planning_dict()` is called**, it returns EMHASS-compatible parameters (nominal power, operating hours, time windows, startup penalty).
- **When start/end condition entities are configured**, `is_start_condition_met` / `is_end_condition_met` evaluate the HA entity state against thresholds.
- **When a condition entity is unavailable/unknown**, the condition evaluates to False (not met).
- **When a boolean entity is checked** ("on"/"true" → 1.0, "off"/"false" → 0.0), numeric comparison applies.
- **When no condition entity is configured**, the condition is always met (True).
- **Time values are normalized**: seconds are stripped ("08:00:30" → "08:00").

### AggregateConstraintAdapter

- **When `max_aggregate_power_kw` is read**, it returns the current power cap for all child adapters combined.
- **This is read-only** — no control commands, only constraint reporting.

### Parent-Child Hierarchy

- **When `add_child(child_id)` is called**, the child is added (no-op if already present).
- **When `remove_child(child_id)` is called**, the child is removed (no-op if not present).
- **Hierarchy is metadata only** — no automatic cascading of commands or state.

### AdapterStatus State Machine

- INITIALIZING → READY (via `async_setup()`)
- READY → ERROR (on unrecoverable failure)
- ERROR → READY (retry `async_setup()`)
- Any → DISABLED (manual, via coordinator)

## Acceptance Criteria

1. All enum values (AdapterType, DeviceClass, ValueType, AdapterStatus) are stable and documented.
2. BaseAdapter subclasses must implement `adapter_type`, `name`, and `async_update()`.
3. ControllableAdapter subclasses must implement `power_capabilities` and `async_set_power()`.
4. `can_accept_power()` correctly validates against rated limits and status.
5. DeferrableLoadAdapter condition evaluation handles all HA entity states (on/off, numeric, unavailable, unknown, missing).
6. `to_planning_dict()` returns valid EMHASS-compatible parameters.
7. PowerCommandResult accurately reports success/failure with timestamps.
8. AdapterData supports both legacy (`value`/`attributes`) and typed (`values` dict) paths.

## Edge Cases

- Mock objects in tests may auto-create attributes — `_cache_key()` must validate types with `isinstance()`.
- `can_accept_power()` does not check device state (SOC, EV connection) — only rated limits and adapter status.
- Condition evaluation: entity state "unavailable" or "unknown" → returns False (unmet).
- Condition evaluation: both `above` and `below` thresholds specified → both must pass.
- `child_ids` property returns a copy (caller cannot mutate internal list).
- `async_update()` may raise exceptions — caller is responsible for catching and setting `_last_error`.
- No automatic retry — coordination layer handles retry logic.
