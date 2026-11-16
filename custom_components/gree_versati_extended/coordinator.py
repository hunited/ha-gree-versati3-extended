"""Coordinator for Gree Versati integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import GreeVersatiClientError, GreeVersatiProtocolClient
from .constants import DOMAIN, POLL_KEYS

_LOGGER = logging.getLogger(__name__)
_RETRY_DELAY_SECONDS = 5


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
            first_error = err
            _LOGGER.debug(
                "Data request failed for %s; retrying in %s seconds: %s",
                DOMAIN,
                _RETRY_DELAY_SECONDS,
                first_error,
            )

        await asyncio.sleep(_RETRY_DELAY_SECONDS)
        try:
            return await self.client.async_get(list(POLL_KEYS))
        except GreeVersatiClientError as retry_error:
            raise UpdateFailed(
                f"Request failed before and after the {_RETRY_DELAY_SECONDS}-second retry: "
                f"{first_error}; {retry_error}"
            ) from retry_error
