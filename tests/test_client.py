"""Basic tests for protocol client helpers."""

from __future__ import annotations

from custom_components.gree_versati_extended.client import (
    ENCRYPTION_ECB,
    ENCRYPTION_GCM,
    GreeVersatiProtocolClient,
)


def test_validate_key_string_accepts_16_bytes() -> None:
    assert GreeVersatiProtocolClient.validate_key_string("1234567890abcdef")


def test_validate_key_string_rejects_non_16_bytes() -> None:
    assert not GreeVersatiProtocolClient.validate_key_string("short")


def test_extract_values_from_opt_and_p() -> None:
    payload = {"opt": ["Pow", "Mod"], "p": [1, 2]}
    values = GreeVersatiProtocolClient._extract_values(payload)
    assert values == {"Pow": 1, "Mod": 2}


def test_extract_values_from_cols_and_dat() -> None:
    payload = {"cols": ["HeWatOutTemSet", "Pow"], "dat": [28, 1]}
    values = GreeVersatiProtocolClient._extract_values(payload)
    assert values == {"HeWatOutTemSet": 28, "Pow": 1}


def test_encrypt_decrypt_roundtrip_ecb() -> None:
    client = GreeVersatiProtocolClient(
        host="127.0.0.1",
        port=7000,
        device_id="502cc62fc0be",
        key="1234567890abcdef",
        timeout=5,
        retries=0,
    )
    payload = {"t": "status", "cols": ["Pow"], "mac": "502cc62fc0be"}
    packed, tag = client._encrypt_pack(payload, ENCRYPTION_ECB)
    unpacked = client._decrypt_pack(packed, tag, ENCRYPTION_ECB)
    assert unpacked == payload


def test_encrypt_decrypt_roundtrip_gcm() -> None:
    client = GreeVersatiProtocolClient(
        host="127.0.0.1",
        port=7000,
        device_id="502cc62fc0be",
        key="1234567890abcdef",
        timeout=5,
        retries=0,
    )
    payload = {"t": "status", "cols": ["Pow"], "mac": "502cc62fc0be"}
    packed, tag = client._encrypt_pack(payload, ENCRYPTION_GCM)
    assert tag is not None
    unpacked = client._decrypt_pack(packed, tag, ENCRYPTION_GCM)
    assert unpacked == payload
