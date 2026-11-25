"""Shared kernel: pure Python, used by every module's domain."""

from rehabgraph.shared.domain.errors import DomainError
from rehabgraph.shared.domain.ids import EntityId, new_id, uuid7

__all__ = ["DomainError", "EntityId", "new_id", "uuid7"]
