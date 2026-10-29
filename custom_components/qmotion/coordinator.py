"""Data coordinator for QMotion hubs."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .protocol import Blind, QMotionClient

_LOGGER = logging.getLogger(__name__)


class QMotionCoordinator(DataUpdateCoordinator[list[Blind]]):
    """Poll the blind inventory from a QSync hub."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        self.client = QMotionClient(host, port)
        super().__init__(hass, _LOGGER, name=f"QMotion {host}", update_interval=timedelta(seconds=60))

    async def _async_update_data(self) -> list[Blind]:
        try:
            return await self.client.async_get_blinds()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with QMotion hub: {err}") from err
