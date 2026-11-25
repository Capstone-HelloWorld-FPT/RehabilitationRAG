"""Entity IDs. Primary keys are UUID v7 (BACKEND-ARCHITECTURE section 7)."""

import os
import time
import uuid
from typing import NewType

EntityId = NewType("EntityId", uuid.UUID)


def uuid7() -> uuid.UUID:
    """Create a UUID v7 (RFC 9562): 48-bit Unix time in ms, then random bits.

    Python 3.12 has no `uuid.uuid7()` (added in 3.14), so it is built with the standard library.
    IDs created later sort after IDs created earlier, which keeps B-tree indexes compact.
    """
    unix_ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")  # 80 random bits, 74 are used
    rand_a = rand >> 68  # 12 bits
    rand_b = rand & ((1 << 62) - 1)  # 62 bits
    value = (unix_ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76  # version 7
    value |= rand_a << 64
    value |= 0b10 << 62  # RFC 4122 / 9562 variant
    value |= rand_b
    return uuid.UUID(int=value)


def new_id() -> EntityId:
    return EntityId(uuid7())
