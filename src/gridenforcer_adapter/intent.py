"""Intent types for plan steps.

An intent describes what the executor should DO with a battery during a slot,
not just the kW number. EMHASS produces per-battery `P_batt` allocations; the
classifier in gridenforcer_emhass turns those (plus system-wide context) into
intents. The executor in gridenforcer_core then picks a strategy per intent —
fixed allocation for grid-driven intents, grid-following for self-consume.
"""

from enum import Enum


class IntentType(Enum):
    """Per-battery intent for a plan step."""

    HOLD = "hold"
    """Battery idle; planned `|P_batt| < BATTERY_DEADBAND_KW`."""

    SELF_CONSUME = "self_consume"
    """Battery charges from system surplus (PV / generator / sister battery).

    Grid is at ~0; executor should grid-follow rather than honor a fixed kW.
    """

    SELF_DISCHARGE = "self_discharge"
    """Battery discharges to cover system deficit (load / sister battery charge).

    Grid is at ~0; executor should grid-follow rather than honor a fixed kW.
    """

    GRID_CHARGE = "grid_charge"
    """Battery charges from grid (price-driven). Executor uses fixed allocation."""

    GRID_DISCHARGE = "grid_discharge"
    """Battery discharges to grid (price-driven). Executor uses fixed allocation."""


GRID_DEADBAND_KW = 0.3
"""Grid power threshold below which a slot is treated as self-consume rather than
grid-charge/discharge."""

BATTERY_DEADBAND_KW = 0.05
"""Battery power threshold below which an allocation is treated as HOLD."""
