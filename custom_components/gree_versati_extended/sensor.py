"""Sensor platform for Gree Versati."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .constants import (
    CONF_DEVICE_ID,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    DIAGNOSTIC_SENSOR_PARAMETERS,
    EXTRA_SENSOR_PARAMETERS,
    PARAM_ALL_ERR,
    PARAM_CO_HOM_TEMP_SET,
    PARAM_CO_WAT_OUT_TEM_SET,
    PARAM_HE_HOM_TEMP_SET,
    PARAM_HE_WAT_OUT_TEM_SET,
    PARAM_MOD,
    PARAM_POW,
    PARAM_TEM_UN,
    PARAM_WAT_BOX_TEM_SET,
    TEMPERATURE_SENSORS,
)
from .coordinator import GreeVersatiCoordinator
from .entity import GreeVersatiEntity


def _decode_temperature(hi: Any, lo: Any) -> float | None:
    """Decode a Hi/Lo temperature pair, returning None for invalid values."""
    if hi is None or lo is None or isinstance(hi, bool) or isinstance(lo, bool):
        return None
    try:
        temperature = float(hi) - 100.0 + float(lo) * 0.1
    except (OverflowError, TypeError, ValueError):
        return None
    if not math.isfinite(temperature):
        return None
    return round(temperature, 1)


@dataclass(frozen=True, kw_only=True)
class GreeVersatiSensorDescription(SensorEntityDescription):
    """Description of a Gree Versati sensor."""

    param_key: str


@dataclass(frozen=True, kw_only=True)
class GreeVersatiTempEntityDescription(SensorEntityDescription):
    """Description of a temperature sensor split into Hi/Lo registers."""

    hi_key: str
    lo_key: str


TEMPERATURE_DESCRIPTIONS: tuple[GreeVersatiTempEntityDescription, ...] = tuple(
    GreeVersatiTempEntityDescription(
        key=key,
        translation_key=key,
        hi_key=hi_key,
        lo_key=lo_key,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    )
    for key, hi_key, lo_key in TEMPERATURE_SENSORS
)

SENSOR_DESCRIPTIONS: tuple[GreeVersatiSensorDescription, ...] = (
    GreeVersatiSensorDescription(
        key="he_wat_out_tem_set",
        translation_key="he_wat_out_tem_set",
        param_key=PARAM_HE_WAT_OUT_TEM_SET,
    ),
    GreeVersatiSensorDescription(
        key="co_hom_tem_set",
        translation_key="co_hom_tem_set",
        param_key=PARAM_CO_HOM_TEMP_SET,
    ),
    GreeVersatiSensorDescription(
        key="he_hom_tem_set",
        translation_key="he_hom_tem_set",
        param_key=PARAM_HE_HOM_TEMP_SET,
    ),
    GreeVersatiSensorDescription(
        key="co_wat_out_tem_set",
        translation_key="co_wat_out_tem_set",
        param_key=PARAM_CO_WAT_OUT_TEM_SET,
    ),
    GreeVersatiSensorDescription(
        key="wat_box_tem_set",
        translation_key="wat_box_tem_set",
        param_key=PARAM_WAT_BOX_TEM_SET,
    ),
    GreeVersatiSensorDescription(
        key="tem_un",
        translation_key="tem_un",
        param_key=PARAM_TEM_UN,
    ),
    GreeVersatiSensorDescription(
        key="all_err",
        translation_key="all_err",
        param_key=PARAM_ALL_ERR,
        entity_registry_enabled_default=PARAM_ALL_ERR
        not in DIAGNOSTIC_SENSOR_PARAMETERS,
    ),
    GreeVersatiSensorDescription(
        key="mod",
        translation_key="mod",
        param_key=PARAM_MOD,
    ),
    GreeVersatiSensorDescription(
        key="pow",
        translation_key="pow",
        param_key=PARAM_POW,
    ),
)

EXTRA_SENSOR_DESCRIPTIONS: tuple[GreeVersatiSensorDescription, ...] = tuple(
    GreeVersatiSensorDescription(
        key=translation_key,
        translation_key=translation_key,
        param_key=param_key,
        entity_registry_enabled_default=param_key not in DIAGNOSTIC_SENSOR_PARAMETERS,
    )
    for param_key, translation_key in EXTRA_SENSOR_PARAMETERS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    runtime_data = hass.data[entry.domain][DATA_ENTRIES][entry.entry_id]
    coordinator = runtime_data[DATA_COORDINATOR]
    device_id = entry.data[CONF_DEVICE_ID]

    async_add_entities(
        [
            *(
                GreeVersatiSensor(coordinator, device_id, description)
                for description in (*SENSOR_DESCRIPTIONS, *EXTRA_SENSOR_DESCRIPTIONS)
            ),
            *(
                GreeVersatiCalculatedTemperatureSensor(coordinator, device_id, description)
                for description in TEMPERATURE_DESCRIPTIONS
            ),
        ]
    )


class GreeVersatiSensor(GreeVersatiEntity, SensorEntity):
    """Represents a generic value sensor from device parameters."""

    entity_description: GreeVersatiSensorDescription

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        description: GreeVersatiSensorDescription,
    ) -> None:
        super().__init__(coordinator, device_id, description.param_key)
        self.entity_description = description

    @property
    def native_value(self) -> str | int | float | bool | None:
        """Return raw protocol value."""
        value = (self.coordinator.data or {}).get(self.entity_description.param_key)
        if isinstance(value, str) and not value.strip():
            return None
        return value


class GreeVersatiCalculatedTemperatureSensor(GreeVersatiEntity, SensorEntity):
    """Temperature in degrees Celsius decoded from a Hi/Lo register pair."""

    entity_description: GreeVersatiTempEntityDescription

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        description: GreeVersatiTempEntityDescription,
    ) -> None:
        super().__init__(coordinator, device_id, description.hi_key, description.key)
        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return if both registers were present in the last response."""
        data = self.coordinator.data or {}
        return (
            self.coordinator.last_update_success
            and self.entity_description.hi_key in data
            and self.entity_description.lo_key in data
        )

    @property
    def native_value(self) -> float | None:
        """Return Hi - 100 plus Lo in tenths of a degree."""
        data = self.coordinator.data or {}
        hi = data.get(self.entity_description.hi_key)
        lo = data.get(self.entity_description.lo_key)
        return _decode_temperature(hi, lo)
