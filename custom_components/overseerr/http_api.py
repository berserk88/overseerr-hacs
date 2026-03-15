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
    """Proxy view — forwards requests to Overseerr server-side, bypassing CORS."""

    url = "/api/overseerr_proxy/{path:.*}"
    name = "api:overseerr_proxy"
    requires_auth = True

    async def get(self, request: web.Request, path: str) -> web.Response:
        return await self._proxy(request, path, "GET")

    async def post(self, request: web.Request, path: str) -> web.Response:
        return await self._proxy(request, path, "POST")

    async def _proxy(self, request: web.Request, path: str, method: str) -> web.Response:
        hass: HomeAssistant = request.app["hass"]

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return self._error(503, "Overseerr integration not configured")

        api = hass.data[DOMAIN].get(entries[0].entry_id)
        if not api:
            return self._error(503, "Overseerr API not available")

        base = api._url.rstrip("/")
        target_url = f"{base}/api/v1/{path}"
        if request.query_string:
            target_url += f"?{request.query_string}"

        _LOGGER.warning("Overseerr proxy %s -> %s", method, target_url)

        try:
            # Use auth-only headers for GET (no Content-Type), JSON headers for POST
            if method == "POST":
                headers = api._json_headers
                try:
                    body = await request.json()
                    kwargs: dict[str, Any] = {"headers": headers, "json": body}
                except Exception:
                    kwargs = {"headers": headers, "data": await request.read()}
            else:
                headers = api._auth_headers
                kwargs = {"headers": headers}

            async with api._session.request(method, target_url, **kwargs) as resp:
                raw = await resp.read()
                if resp.status >= 400:
                    _LOGGER.warning(
                        "Overseerr %s %s returned %s: %s",
                        method, target_url, resp.status, raw[:500]
                    )
                # Use application/json as content type — Overseerr always returns JSON
                return web.Response(
                    status=resp.status,
                    content_type="application/json",
                    body=raw,
                )

        except Exception as err:
            _LOGGER.error("Overseerr proxy error %s %s: %s", method, target_url, err)
            return self._error(502, str(err))

    @staticmethod
    def _error(status: int, message: str) -> web.Response:
        return web.Response(
            status=status,
            content_type="application/json",
            text=json.dumps({"error": message}),
        )
