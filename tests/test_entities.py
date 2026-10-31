"""Tests for protocol values exposed by entities."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from custom_components.gree_versati_extended.constants import (
    BOOLEAN_SENSOR_PARAMETERS,
    DEFAULT_SCAN_INTERVAL,
    DIAGNOSTIC_SENSOR_PARAMETERS,
    EXTRA_SENSOR_PARAMETERS,
    MODE_OPTIONS,
    PARAM_CO_HOM_TEMP_SET,
    PARAM_CO_WAT_OUT_TEM_SET,
    PARAM_HE_HOM_TEMP_SET,
    PARAM_HE_WAT_OUT_TEM_SET,
    PARAM_MOD,
    PARAM_POW,
    PARAM_WAT_BOX_TEM_SET,
    POLL_KEYS,
)
from custom_components.gree_versati_extended.sensor import (
    EXTRA_SENSOR_DESCRIPTIONS,
    SENSOR_DESCRIPTIONS,
    TEMPERATURE_DESCRIPTIONS,
    _decode_temperature,
    _format_boolean_state,
    _format_temperature_unit,
)
from custom_components.gree_versati_extended.number import SETPOINT_DEFINITIONS
from custom_components.gree_versati_extended.select import GreeVersatiModeSelect
from custom_components.gree_versati_extended.switch import GreeVersatiPowerSwitch
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


@pytest.mark.parametrize(
    ("value", "language", "expected"),
    [
        (0, "en", "Off"),
        (1, "en", "On"),
        (0, "hu", "Ki"),
        (1, "hu-HU", "Be"),
        (2, "en", None),
        ("invalid", "hu", None),
    ],
)
def test_format_boolean_sensor_state(
    value: object,
    language: str,
    expected: str | None,
) -> None:
    assert _format_boolean_state(value, language) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, "°C"), ("0", "°C"), (1, "°F"), ("1", "°F"), (2, None), (True, None)],
)
def test_format_temperature_unit(value: object, expected: str | None) -> None:
    assert _format_temperature_unit(value) == expected


def test_default_scan_interval_is_five_minutes() -> None:
    assert DEFAULT_SCAN_INTERVAL == 300


def test_control_values_are_not_exposed_as_duplicate_sensors() -> None:
    sensor_parameters = {
        description.param_key for description in SENSOR_DESCRIPTIONS
    } | {description.param_key for description in EXTRA_SENSOR_DESCRIPTIONS}

    assert not sensor_parameters.intersection(
        {
            PARAM_HE_WAT_OUT_TEM_SET,
            PARAM_CO_WAT_OUT_TEM_SET,
            PARAM_WAT_BOX_TEM_SET,
            PARAM_HE_HOM_TEMP_SET,
            PARAM_CO_HOM_TEMP_SET,
            PARAM_MOD,
            PARAM_POW,
        }
    )


def test_control_and_temperature_entities_have_domain_icons() -> None:
    icons_by_parameter = {
        definition["param"]: definition["icon"]
        for definition in SETPOINT_DEFINITIONS
    }

    assert icons_by_parameter[PARAM_HE_WAT_OUT_TEM_SET] == "mdi:sun-thermometer"
    assert icons_by_parameter[PARAM_CO_WAT_OUT_TEM_SET] == "mdi:snowflake-thermometer"
    assert icons_by_parameter[PARAM_HE_HOM_TEMP_SET] == "mdi:sun-thermometer"
    assert icons_by_parameter[PARAM_CO_HOM_TEMP_SET] == "mdi:snowflake-thermometer"
    power_switch = GreeVersatiPowerSwitch(MagicMock(), "device", MagicMock())
    mode_select = GreeVersatiModeSelect(MagicMock(), "device", MagicMock())
    assert power_switch.icon == "mdi:heat-pump"
    assert mode_select.icon == "mdi:hvac"
    assert {description.icon for description in TEMPERATURE_DESCRIPTIONS} == {
        "mdi:water-thermometer",
        "mdi:thermometer-chevron-up",
        "mdi:thermometer-chevron-down",
        "mdi:thermometer",
        "mdi:home-thermometer",
    }


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

        mode_states = translations["entity"]["select"]["mode_control"]["state"]
        assert set(mode_states) == set(MODE_OPTIONS)
        assert all(mode_states.values())


def test_binary_sensor_parameters_are_explicitly_defined() -> None:
    extra_sensor_keys = {param_key for param_key, _ in EXTRA_SENSOR_PARAMETERS}
    assert BOOLEAN_SENSOR_PARAMETERS <= extra_sensor_keys


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
