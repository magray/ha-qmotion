"""Cover entities for QMotion blinds."""

from datetime import datetime, timezone

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import QMotionCoordinator
from .const import DOMAIN, SUPPORTED_POSITIONS
from .protocol import Blind


def _nearest_preset(position: float) -> float:
    return min(SUPPORTED_POSITIONS, key=lambda candidate: abs(candidate - position))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: QMotionCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(QMotionCover(coordinator, entry, blind) for blind in coordinator.data)


class QMotionCover(CoordinatorEntity[QMotionCoordinator], CoverEntity, RestoreEntity):
    """A QMotion blind group with estimated position tracking."""

    _attr_has_entity_name = True
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION | CoverEntityFeature.STOP
    _attr_device_class = "blind"

    def __init__(self, coordinator: QMotionCoordinator, entry: ConfigEntry, blind: Blind) -> None:
        super().__init__(coordinator)
        self._blind = blind
        # The device name is the QMotion group name; avoid duplicating it as the entity name.
        self._attr_name = None
        self._attr_unique_id = f"{entry.entry_id}_{blind.address}"
        self._attr_is_closed = False
        self._attr_current_cover_position = None
        self._attr_extra_state_attributes = {
            "qmotion_address": blind.address,
            "qmotion_group_name": blind.name,
        }
        self._motion_started = None
        self._motion_from = 0.0
        self._motion_to = 0.0

    @property
    def device_info(self):
        """Expose each named QMotion group as an independently assignable HA device."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.host, self._blind.address)},
            "name": self._blind.name,
            "manufacturer": "QMotion",
            "model": "QMotion Blind Group",
            "configuration_url": f"http://{self.coordinator.client.host}",
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is not None:
            try:
                position = float(state.attributes.get("current_position"))
            except (TypeError, ValueError):
                return
            self._attr_current_cover_position = int(_nearest_preset(position))
            self._attr_is_closed = self._attr_current_cover_position == 0

    @property
    def current_cover_position(self) -> int | None:
        if self._motion_started is not None:
            elapsed = (datetime.now(timezone.utc) - self._motion_started).total_seconds()
            fraction = min(1.0, elapsed / 30.0)
            position = self._motion_from + (self._motion_to - self._motion_from) * fraction
            self._attr_current_cover_position = int(round(_nearest_preset(position)))
            if fraction >= 1:
                self._motion_started = None
                self._attr_is_closed = self._attr_current_cover_position == 0
        return self._attr_current_cover_position

    @property
    def is_closed(self) -> bool | None:
        return self.current_cover_position == 0 if self.current_cover_position is not None else None

    async def async_open_cover(self, **kwargs) -> None:
        await self.async_set_cover_position(position=100)

    async def async_close_cover(self, **kwargs) -> None:
        await self.async_set_cover_position(position=0)

    async def async_set_cover_position(self, **kwargs) -> None:
        target = _nearest_preset(max(0, min(100, float(kwargs["position"]))))
        current = self.current_cover_position
        await self.coordinator.client.async_move(self._blind.address, target)
        self._motion_from = float(current if current is not None else 0)
        self._motion_to = target
        self._motion_started = datetime.now(timezone.utc)
        self._attr_is_closed = target == 0
        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs) -> None:
        current = self.current_cover_position
        if current is not None:
            await self.coordinator.client.async_move(self._blind.address, current)
        self._motion_started = None
        self.async_write_ha_state()
