"""The Gree Versati Local Extended integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .client import GreeVersatiProtocolClient
from .constants import (
    CONF_DEVICE_ID,
    CONF_KEY,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    DEFAULT_RETRIES,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    SERVICE_SET_PARAM,
)
from .coordinator import GreeVersatiCoordinator
from .services import async_register_services, async_unregister_services


GreeVersatiConfigEntry = ConfigEntry


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration from YAML (not used)."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_ENTRIES, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GreeVersatiConfigEntry) -> bool:
    """Set up Gree Versati from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_ENTRIES, {})

    client = GreeVersatiProtocolClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        device_id=entry.data[CONF_DEVICE_ID],
        key=entry.data[CONF_KEY],
        timeout=float(entry.data[CONF_TIMEOUT]),
        retries=DEFAULT_RETRIES,
    )

    scan_interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    coordinator = GreeVersatiCoordinator(hass, client, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][DATA_ENTRIES][entry.entry_id] = {
        DATA_CLIENT: client,
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_SET_PARAM):
        await async_register_services(hass)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GreeVersatiConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN][DATA_ENTRIES].pop(entry.entry_id, None)

    if not hass.data[DOMAIN][DATA_ENTRIES]:
        await async_unregister_services(hass)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: GreeVersatiConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
