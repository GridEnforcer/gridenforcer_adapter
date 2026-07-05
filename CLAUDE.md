# CLAUDE.md

Project-specific guidance for Claude Code in this repo.

## Shared team workflow

These rules apply to all GridEnforcer repos and are maintained in the sibling repo `gridenforcer_planning` (clone it next to this repo — it also holds the Beads issue database):

@../gridenforcer_planning/workflow/dev-stage.md
@../gridenforcer_planning/workflow/uv-setup.md
@../gridenforcer_planning/workflow/beads.md
@../gridenforcer_planning/workflow/planning-discipline.md
@../gridenforcer_planning/workflow/dod.md

## Project

Shared adapter base package consumed by every GridEnforcer integration: `BaseAdapter`, `ControllableAdapter`, `AdapterType`, `DeviceClass`, `ValueType`, `AdapterData`, `DeferrableLoadAdapter`.

All sibling repos install this package as an editable local override (`[tool.uv.sources]`), so **changes here immediately affect every adapter repo and Core** — run their test suites when touching the base contract.

### Adapter type system

| Adapter | adapter_type | device_class | Key ValueTypes |
|---------|-------------|--------------|----------------|
| Grid meter | METER | GRID_METER | GRID_POWER, GRID_IMPORT_POWER, GRID_EXPORT_POWER |
| Consumption | METER | LOAD_METER | LOAD_POWER |
| Production | PRODUCTION | SOLAR_INVERTER | POWER |
| Storage | STORAGE | HOME_BATTERY / EV_CHARGER | SOC, BATTERY_POWER, CAPACITY |
| Grid price | GRID_PRICE | GENERIC | ENERGY_PRICE, PRICE_FORECAST |
| Deferrable | DEFERRABLE | GENERIC / HEAT_PUMP | — (uses `to_planning_dict()`) |

`AdapterData.values: dict[ValueType, float | list | None]` — typed values dict.
`AdapterState.get_value(key)` — typed lookup with attributes fallback.

## Commands

```bash
uv run pytest tests/ --tb=no -q
uv run ruff check src/
uv run mypy src/
```
