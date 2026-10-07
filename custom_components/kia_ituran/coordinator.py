"""Data update coordinator."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnect, InvalidAuth, async_fetch_electric_data
from .const import CONF_PLATFORM_ID, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class KiaIturanCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Fetch electric data from Ituran."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        data = self.config_entry.data
        try:
            return await async_fetch_electric_data(
                async_get_clientsession(self.hass),
                data[CONF_USERNAME],
                data[CONF_PASSWORD],
                data[CONF_PLATFORM_ID],
            )
        except (CannotConnect, InvalidAuth) as err:
            raise UpdateFailed(str(err)) from err
