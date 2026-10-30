"""Tests for protocol values exposed by entities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from custom_components.gree_versati_extended.constants import (
    DIAGNOSTIC_SENSOR_PARAMETERS,
    EXTRA_SENSOR_PARAMETERS,
    POLL_KEYS,
)
from custom_components.gree_versati_extended.sensor import (
    EXTRA_SENSOR_DESCRIPTIONS,
    SENSOR_DESCRIPTIONS,
    _decode_temperature,
)
from custom_components.gree_versati_extended.switch import _parse_switch_state


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, False),
        (1, True),
        (False, False),
        (True, True),
        ("0", False),
        ("1", True),
        ("false", False),
        ("true", True),
        ("off", False),
        ("on", True),
        (" false ", False),
        ("unknown", None),
        (2, None),
        (None, None),
    ],
)
def test_parse_switch_state(value: object, expected: bool | None) -> None:
    assert _parse_switch_state(value) is expected


@pytest.mark.parametrize(
    ("hi", "lo", "expected"),
    [
        (123, 2, 23.2),
        (123, 6, 23.6),
        (123, 0, 23.0),
        (150, 2, 50.2),
        (122, 3, 22.3),
    ],
)
def test_decode_temperature(hi: int, lo: int, expected: float) -> None:
    assert _decode_temperature(hi, lo) == expected


@pytest.mark.parametrize(
    ("hi", "lo"),
    [
        ("invalid", 5),
        (100, "invalid"),
        (None, 5),
        (100, None),
        (True, 5),
    ],
)
def test_decode_temperature_returns_none_for_invalid_values(
    hi: object,
    lo: object,
) -> None:
    assert _decode_temperature(hi, lo) is None


def test_extra_parameters_are_polled_and_have_english_and_hungarian_names() -> None:
    integration_dir = (
        Path(__file__).parents[1] / "custom_components" / "gree_versati_extended"
    )
    expected_parameters = {param_key for param_key, _ in EXTRA_SENSOR_PARAMETERS}
    descriptions_by_parameter = {
        description.param_key: description
        for description in EXTRA_SENSOR_DESCRIPTIONS
    }

    assert expected_parameters <= set(POLL_KEYS)
    assert expected_parameters == set(descriptions_by_parameter)

    for translation_file in (
        integration_dir / "strings.json",
        integration_dir / "translations" / "en.json",
        integration_dir / "translations" / "hu.json",
    ):
        translations = json.loads(translation_file.read_text(encoding="utf-8"))
        sensor_translations = translations["entity"]["sensor"]
        for description in EXTRA_SENSOR_DESCRIPTIONS:
            assert description.translation_key in sensor_translations
            assert sensor_translations[description.translation_key]["name"]


def test_diagnostic_entities_are_disabled_by_default() -> None:
    descriptions = (*SENSOR_DESCRIPTIONS, *EXTRA_SENSOR_DESCRIPTIONS)
    descriptions_by_parameter = {
        description.param_key: description for description in descriptions
    }

    assert DIAGNOSTIC_SENSOR_PARAMETERS <= descriptions_by_parameter.keys()
    assert all(
        not descriptions_by_parameter[param_key].entity_registry_enabled_default
        for param_key in DIAGNOSTIC_SENSOR_PARAMETERS
    )
    assert all(
        descriptions_by_parameter[description.param_key].entity_registry_enabled_default
        for description in EXTRA_SENSOR_DESCRIPTIONS
        if description.param_key not in DIAGNOSTIC_SENSOR_PARAMETERS
    )
