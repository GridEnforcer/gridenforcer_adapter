"""GridEnforcer adapter base classes for Home Assistant integrations.

This package provides the base adapter interface for energy management integrations
in Home Assistant. It defines a common contract for data sources (grid prices,
production, consumption, storage, etc.) that can be used by decision engines.

Example usage:
    from gridenforcer_adapter import BaseAdapter, AdapterData, AdapterType

    class MyCustomAdapter(BaseAdapter):
        @property
        def adapter_type(self) -> AdapterType:
            return AdapterType.CUSTOM

        @property
        def name(self) -> str:
            return "My Custom Adapter"

        async def async_update(self) -> AdapterData:
            # Fetch data from your source
            return AdapterData(
                value=42.0,
                unit="kWh",
                timestamp=datetime.now(),
            )
"""

from .aggregate import AggregateConstraintAdapter
from .base import AdapterData, AdapterStatus, AdapterType, BaseAdapter
from .controllable import ControllableAdapter, PowerCapabilities, PowerCommandResult

__version__ = "0.2.0"
__all__ = [
    "BaseAdapter",
    "AdapterData",
    "AdapterType",
    "AdapterStatus",
    "ControllableAdapter",
    "PowerCapabilities",
    "PowerCommandResult",
    "AggregateConstraintAdapter",
]
