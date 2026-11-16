"""Tests for coordinator data polling."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.gree_versati_extended import coordinator as coordinator_module
from custom_components.gree_versati_extended.client import GreeVersatiClientError
from custom_components.gree_versati_extended.constants import POLL_KEYS
from custom_components.gree_versati_extended.coordinator import GreeVersatiCoordinator


def _make_coordinator(client: MagicMock) -> GreeVersatiCoordinator:
    coordinator = object.__new__(GreeVersatiCoordinator)
    coordinator.client = client
    return coordinator


def test_coordinator_retries_after_five_seconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MagicMock()
    client.async_get = AsyncMock(
        side_effect=[GreeVersatiClientError("timeout"), {"Pow": 1}]
    )
    sleep = AsyncMock()
    monkeypatch.setattr(coordinator_module.asyncio, "sleep", sleep)
    coordinator = _make_coordinator(client)

    result = asyncio.run(coordinator._async_update_data())

    assert result == {"Pow": 1}
    client.async_get.assert_has_awaits(
        [call(list(POLL_KEYS)), call(list(POLL_KEYS))]
    )
    sleep.assert_awaited_once_with(5)


def test_coordinator_fails_only_after_retry_also_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MagicMock()
    client.async_get = AsyncMock(
        side_effect=[
            GreeVersatiClientError("first timeout"),
            GreeVersatiClientError("second timeout"),
        ]
    )
    sleep = AsyncMock()
    monkeypatch.setattr(coordinator_module.asyncio, "sleep", sleep)
    coordinator = _make_coordinator(client)

    with pytest.raises(UpdateFailed, match="first timeout; second timeout"):
        asyncio.run(coordinator._async_update_data())

    assert client.async_get.await_count == 2
    sleep.assert_awaited_once_with(5)
