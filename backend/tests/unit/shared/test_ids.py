from rehabgraph.shared.domain import uuid7


def test_uuid7_has_version_7_and_rfc_variant() -> None:
    value = uuid7()
    assert value.version == 7
    assert value.variant == "specified in RFC 4122"


def test_uuid7_sorts_by_creation_time() -> None:
    ids = [uuid7() for _ in range(200)]
    timestamps = [i.int >> 80 for i in ids]
    assert timestamps == sorted(timestamps)


def test_uuid7_is_unique() -> None:
    assert len({uuid7() for _ in range(1000)}) == 1000
