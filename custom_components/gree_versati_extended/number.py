"""Number platform for Gree Versati."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import GreeVersatiProtocolClient
from .constants import (
    CO_HOM_TEMP_SET_STEP,
    CO_WAT_OUT_TEMP_SET_STEP,
    CONF_DEVICE_ID,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    HE_HOM_TEMP_SET_STEP,
    HE_WAT_OUT_TEMP_SET_STEP,
    MAX_CO_HOM_TEMP_SET,
    MAX_CO_WAT_OUT_TEMP_SET,
    MAX_HE_HOM_TEMP_SET,
    MAX_HE_WAT_OUT_TEMP_SET,
    MAX_WAT_BOX_TEMP_SET,
    MIN_CO_HOM_TEMP_SET,
    MIN_CO_WAT_OUT_TEMP_SET,
    MIN_HE_HOM_TEMP_SET,
    MIN_HE_WAT_OUT_TEMP_SET,
    MIN_WAT_BOX_TEMP_SET,
    PARAM_CO_HOM_TEMP_SET,
    PARAM_CO_WAT_OUT_TEM_SET,
    PARAM_HE_HOM_TEMP_SET,
    PARAM_HE_WAT_OUT_TEM_SET,
    PARAM_WAT_BOX_TEM_SET,
    WAT_BOX_TEMP_SET_STEP,
)
from .coordinator import GreeVersatiCoordinator
from .entity import GreeVersatiEntity

SETPOINT_DEFINITIONS = [
    {
        "param": PARAM_HE_WAT_OUT_TEM_SET,
        "translation_key": "he_wat_out_tem_set",
        "icon": "mdi:sun-thermometer",
        "min": MIN_HE_WAT_OUT_TEMP_SET,
        "max": MAX_HE_WAT_OUT_TEMP_SET,
        "step": HE_WAT_OUT_TEMP_SET_STEP,
    },
    {
        "param": PARAM_CO_WAT_OUT_TEM_SET,
        "translation_key": "co_wat_out_tem_set",
        "icon": "mdi:snowflake-thermometer",
        "min": MIN_CO_WAT_OUT_TEMP_SET,
        "max": MAX_CO_WAT_OUT_TEMP_SET,
        "step": CO_WAT_OUT_TEMP_SET_STEP,
    },
    {
        "param": PARAM_WAT_BOX_TEM_SET,
        "translation_key": "wat_box_tem_set",
        "icon": "mdi:water-thermometer",
        "min": MIN_WAT_BOX_TEMP_SET,
        "max": MAX_WAT_BOX_TEMP_SET,
        "step": WAT_BOX_TEMP_SET_STEP,
    },
    {
        "param": PARAM_HE_HOM_TEMP_SET,
        "translation_key": "he_hom_tem_set",
        "icon": "mdi:sun-thermometer",
        "min": MIN_HE_HOM_TEMP_SET,
        "max": MAX_HE_HOM_TEMP_SET,
        "step": HE_HOM_TEMP_SET_STEP,
    },
    {
        "param": PARAM_CO_HOM_TEMP_SET,
        "translation_key": "co_hom_tem_set",
        "icon": "mdi:snowflake-thermometer",
        "min": MIN_CO_HOM_TEMP_SET,
        "max": MAX_CO_HOM_TEMP_SET,
        "step": CO_HOM_TEMP_SET_STEP,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities dynamically."""
    runtime_data = hass.data[entry.domain][DATA_ENTRIES][entry.entry_id]
    coordinator = runtime_data[DATA_COORDINATOR]
    client = runtime_data[DATA_CLIENT]
    device_id = entry.data[CONF_DEVICE_ID]

    async_add_entities(
        GreeVersatiSetpointNumber(coordinator, device_id, client, definition)
        for definition in SETPOINT_DEFINITIONS
    )


class GreeVersatiSetpointNumber(GreeVersatiEntity, NumberEntity):
    """Universal configurable setpoint number entity."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = "box"

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
        definition: dict[str, Any],
    ) -> None:
        param_key = definition["param"]
        super().__init__(coordinator, device_id, param_key)
        self._client = client
        self._attr_translation_key = definition["translation_key"]
        self._attr_icon = definition["icon"]
        self._attr_native_min_value = definition["min"]
        self._attr_native_max_value = definition["max"]
        self._attr_native_step = definition["step"]

    @property
    def native_value(self) -> float | None:
        """Return current setpoint value."""
        value = (self.coordinator.data or {}).get(self._param_key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set setpoint value."""
        target_value = int(round(value))
        await self._client.async_set({self._param_key: target_value})

        # The heat pump can briefly report the old value after accepting a setpoint.
        updated_data = dict(self.coordinator.data or {})
        updated_data[self._param_key] = target_value
        self.coordinator.async_set_updated_data(updated_data)
