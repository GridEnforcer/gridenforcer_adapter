"""Aggregate constraint adapter for hierarchical power limits."""

from abc import abstractmethod

from .base import AdapterType, BaseAdapter


class AggregateConstraintAdapter(BaseAdapter):
    """Base class for aggregate power constraint adapters.

    These adapters represent read-only aggregate power limits that constrain
    the sum of allocations to child adapters.

    Examples: Plant-level inverter limits, building-level circuit limits,
    system-level power caps.
    """

    @property
    def adapter_type(self) -> AdapterType:
        """Return aggregate constraint type."""
        return AdapterType.AGGREGATE

    @property
    @abstractmethod
    def max_aggregate_power_kw(self) -> float:
        """Return current maximum aggregate power limit in kW.

        This is the aggregate constraint applied to all children.
        ExecutionEngine will scale child allocations if their sum exceeds this.
        """
