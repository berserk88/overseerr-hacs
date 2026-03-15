"""Overseerr API client."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class OverseerrAPI:
    """Overseerr API client."""

    def __init__(self, url: str, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._session = session
        # Only the API key header — Content-Type is added per-request only when needed
        self._auth_headers = {
            "X-Api-Key": api_key,
        }
        # Headers for requests with a JSON body
        self._json_headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an API request."""
        url = f"{self._url}/api/v1{endpoint}"
        # Use JSON headers only for POST/PUT/PATCH, plain auth for GET/DELETE
        if method.upper() in ("POST", "PUT", "PATCH"):
            headers = self._json_headers
        else:
            headers = self._auth_headers
        try:
            async with self._session.request(
                method, url, headers=headers, **kwargs
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("API request failed [%s] %s: %s", method, url, err)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error [%s] %s: %s", method, url, err)
            raise

    async def get_status(self) -> dict:
        """Get Overseerr server status."""
        return await self._request("GET", "/status")

    async def search(self, query: str, page: int = 1) -> dict:
        """Search for movies and TV shows."""
        return await self._request(
            "GET",
            "/search",
            params={"query": query, "page": page},
        )

    async def get_movie(self, movie_id: int) -> dict:
        """Get movie details."""
        return await self._request("GET", f"/movie/{movie_id}")

    async def get_tv(self, tv_id: int) -> dict:
        """Get TV show details."""
        return await self._request("GET", f"/tv/{tv_id}")

    async def request_media(self, media_type: str, media_id: int, seasons: list | None = None) -> dict:
        """Request a movie or TV show."""
        payload: dict[str, Any] = {
            "mediaType": media_type,
            "mediaId": media_id,
        }
        if media_type == "tv":
            payload["seasons"] = seasons if seasons else "all"
        return await self._request("POST", "/request", json=payload)

    async def get_requests(self, take: int = 20, skip: int = 0, filter: str = "all") -> dict:
        """Get list of media requests."""
        return await self._request(
            "GET",
            "/request",
            params={"take": take, "skip": skip, "filter": filter},
        )

    async def get_pending_requests_count(self) -> int:
        """Get count of pending requests."""
        result = await self._request(
            "GET",
            "/request",
            params={"take": 1, "skip": 0, "filter": "pending"},
        )
        return result.get("pageInfo", {}).get("results", 0)

    async def get_trending(self) -> dict:
        """Get trending movies and TV shows."""
        return await self._request("GET", "/discover/trending")

    async def get_popular_movies(self) -> dict:
        """Get popular movies."""
        return await self._request("GET", "/discover/movies")

    async def get_popular_tv(self) -> dict:
        """Get popular TV shows."""
        return await self._request("GET", "/discover/tv")

    async def approve_request(self, request_id: int) -> dict:
        """Approve a request."""
        return await self._request("POST", f"/request/{request_id}/approve")

    async def decline_request(self, request_id: int) -> dict:
        """Decline a request."""
        return await self._request("POST", f"/request/{request_id}/decline")
