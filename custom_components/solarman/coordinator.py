from __future__ import annotations

import logging
import asyncio

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import *

_LOGGER = logging.getLogger(__name__)

class InverterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, inverter):
        super().__init__(hass, _LOGGER, name = SENSOR_PREFIX, update_interval = TIMINGS_COORDINATOR, always_update = False)
        self.inverter = inverter
        self.counter = -1

    def _accounting(self):
        if self.last_update_success:
            self.counter += 1

        # Temporary fix to retrieve all data after disconnect
        if self.inverter.status != 1:
            self.counter = 0

        return int(self.counter * self._update_interval_seconds)

    async def _async_update_data(self) -> dict[str, Any]:
        async with asyncio.timeout(TIMINGS_COORDINATOR_TIMEOUT):
            return await self.inverter.async_get(self._accounting())

    #async def _reload(self):
    #    _LOGGER.debug('_reload')
    #    await self.hass.services.async_call("homeassistant", "reload_config_entry", { "entity_id": "???" }, blocking = False)

    async def async_shutdown(self) -> None:
        _LOGGER.debug("async_shutdown")
        await super().async_shutdown()
        await self.inverter.async_disconnect()