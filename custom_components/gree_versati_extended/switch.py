"""Switch platform for Gree Versati Extended."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import GreeVersatiProtocolClient
from .constants import (
    CONF_DEVICE_ID,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    PARAM_POW,
    PARAM_QUIET,
)
from .coordinator import GreeVersatiCoordinator
from .entity import GreeVersatiEntity


def _parse_switch_state(value: Any) -> bool | None:
    """Convert recognized protocol values to a boolean switch state."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value in (0, 1):
            return bool(value)
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "on"}:
            return True
        if normalized in {"0", "false", "off"}:
            return False
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    runtime_data = hass.data[entry.domain][DATA_ENTRIES][entry.entry_id]
    async_add_entities(
        [
            GreeVersatiPowerSwitch(
                runtime_data[DATA_COORDINATOR],
                entry.data[CONF_DEVICE_ID],
                runtime_data[DATA_CLIENT],
            ),
            GreeVersatiQuietSwitch(
                runtime_data[DATA_COORDINATOR],
                entry.data[CONF_DEVICE_ID],
                runtime_data[DATA_CLIENT],
            ),
        ]
    )


class GreeVersatiPowerSwitch(GreeVersatiEntity, SwitchEntity):
    """Power control switch."""

    _attr_translation_key = "power_control"
    _attr_icon = "mdi:heat-pump"

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            PARAM_POW,
            unique_id_key="power_switch",
        )
        self._client = client

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        value = (self.coordinator.data or {}).get(PARAM_POW)
        return _parse_switch_state(value)

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn on power."""
        await self._client.async_set({PARAM_POW: 1})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off power."""
        await self._client.async_set({PARAM_POW: 0})
        await self.coordinator.async_request_refresh()


class GreeVersatiQuietSwitch(GreeVersatiEntity, SwitchEntity):
    """Quiet mode control switch."""

    _attr_translation_key = "quiet_mode"

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            PARAM_QUIET,
            unique_id_key="quiet_switch",
        )
        self._client = client

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        value = (self.coordinator.data or {}).get(PARAM_QUIET)
        return _parse_switch_state(value)

    @property
    def icon(self) -> str:
        """Return icon matching the state."""
        return "mdi:volume-off" if self.is_on else "mdi:volume-high"

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn on quiet mode."""
        await self._client.async_set({PARAM_QUIET: 1})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off quiet mode."""
        await self._client.async_set({PARAM_QUIET: 0})
        await self.coordinator.async_request_refresh()
