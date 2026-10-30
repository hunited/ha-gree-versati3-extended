"""Coordinator for Gree Versati integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import GreeVersatiClientError, GreeVersatiProtocolClient
from .constants import DOMAIN, POLL_KEYS

_LOGGER = logging.getLogger(__name__)


class GreeVersatiCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch data from Gree Versati Extended device periodically."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: GreeVersatiProtocolClient,
        scan_interval_seconds: int,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval_seconds),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get(list(POLL_KEYS))
        except GreeVersatiClientError as err:
            raise UpdateFailed(str(err)) from err
