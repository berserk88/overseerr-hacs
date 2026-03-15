"""Sensor platform for Overseerr integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .api import OverseerrAPI

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Overseerr sensor from a config entry."""
    api: OverseerrAPI = hass.data[DOMAIN][config_entry.entry_id]

    coordinator = OverseerrDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        OverseerrPendingRequestsSensor(coordinator, config_entry),
        OverseerrTotalRequestsSensor(coordinator, config_entry),
    ])


class OverseerrDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Overseerr data updates."""

    def __init__(self, hass: HomeAssistant, api: OverseerrAPI) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from Overseerr."""
        try:
            pending = await self.api.get_requests(filter="pending")
            all_requests = await self.api.get_requests(filter="all")
            return {
                "pending_count": pending.get("pageInfo", {}).get("results", 0),
                "total_count": all_requests.get("pageInfo", {}).get("results", 0),
                "recent_requests": all_requests.get("results", [])[:5],
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Overseerr: {err}") from err


class OverseerrPendingRequestsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for pending Overseerr requests."""

    _attr_icon = "mdi:clock-outline"
    _attr_name = "Overseerr Pending Requests"

    def __init__(self, coordinator: OverseerrDataCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_pending_requests"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("pending_count", 0)

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "recent_requests": self.coordinator.data.get("recent_requests", [])
        }


class OverseerrTotalRequestsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total Overseerr requests."""

    _attr_icon = "mdi:movie-open"
    _attr_name = "Overseerr Total Requests"

    def __init__(self, coordinator: OverseerrDataCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_requests"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("total_count", 0)
