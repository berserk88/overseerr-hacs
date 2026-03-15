"""Overseerr integration for Home Assistant."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_URL, CONF_API_KEY
from .api import OverseerrAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Overseerr component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Overseerr from a config entry."""
    session = async_get_clientsession(hass)
    api = OverseerrAPI(
        url=entry.data[CONF_URL],
        api_key=entry.data[CONF_API_KEY],
        session=session,
    )

    # Verify connection
    try:
        await api.get_status()
    except Exception as err:
        _LOGGER.error("Failed to connect to Overseerr: %s", err)
        return False

    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_request_media(call):
        """Handle the request_media service call."""
        media_type = call.data.get("media_type")
        media_id = call.data.get("media_id")
        result = await api.request_media(media_type, media_id)
        _LOGGER.info("Media request result: %s", result)

    async def handle_search(call):
        """Handle the search service call."""
        query = call.data.get("query")
        results = await api.search(query)
        hass.bus.async_fire(
            f"{DOMAIN}_search_results",
            {"query": query, "results": results}
        )

    hass.services.async_register(DOMAIN, "request_media", handle_request_media)
    hass.services.async_register(DOMAIN, "search", handle_search)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
