"""HTTP API proxy views for Overseerr integration."""
from __future__ import annotations

import logging
import json
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def async_register_views(hass: HomeAssistant) -> None:
    """Register the Overseerr proxy HTTP views."""
    hass.http.register_view(OverseerrProxyView)


class OverseerrProxyView(HomeAssistantView):
    """Proxy view that forwards requests to Overseerr server-side (bypasses CORS)."""

    url = "/api/overseerr_proxy/{path:.*}"
    name = "api:overseerr_proxy"
    requires_auth = True  # HA login required — the card uses the HA token automatically

    async def get(self, request: web.Request, path: str) -> web.Response:
        """Handle GET proxy requests."""
        return await self._proxy(request, path, "GET")

    async def post(self, request: web.Request, path: str) -> web.Response:
        """Handle POST proxy requests."""
        return await self._proxy(request, path, "POST")

    async def _proxy(self, request: web.Request, path: str, method: str) -> web.Response:
        """Forward the request to Overseerr and return the response."""
        hass: HomeAssistant = request.app["hass"]

        # Get the first configured Overseerr entry
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return web.Response(
                status=503,
                content_type="application/json",
                text=json.dumps({"error": "Overseerr integration not configured"}),
            )

        api = hass.data[DOMAIN].get(entries[0].entry_id)
        if not api:
            return web.Response(
                status=503,
                content_type="application/json",
                text=json.dumps({"error": "Overseerr API not available"}),
            )

        # Build the target URL, preserving query string
        query_string = request.query_string
        target_url = f"{api._url}/api/v1/{path}"
        if query_string:
            target_url += f"?{query_string}"

        try:
            kwargs: dict[str, Any] = {"headers": api._headers}

            if method == "POST":
                try:
                    body = await request.json()
                    kwargs["json"] = body
                except Exception:
                    kwargs["data"] = await request.read()

            async with api._session.request(method, target_url, **kwargs) as resp:
                raw = await resp.read()
                return web.Response(
                    status=resp.status,
                    content_type="application/json",
                    body=raw,
                )
        except Exception as err:
            _LOGGER.error("Overseerr proxy error for %s %s: %s", method, target_url, err)
            return web.Response(
                status=502,
                content_type="application/json",
                text=json.dumps({"error": str(err)}),
            )
