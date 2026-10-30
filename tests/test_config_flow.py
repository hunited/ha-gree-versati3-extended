"""Basic tests for config flow related validation."""

from __future__ import annotations

from custom_components.gree_versati_extended.client import GreeVersatiProtocolClient


def test_key_validation_uses_utf8_byte_length() -> None:
    assert GreeVersatiProtocolClient.validate_key_string("1234567890abcdef") is True
    assert GreeVersatiProtocolClient.validate_key_string("1234567890abcde") is False
