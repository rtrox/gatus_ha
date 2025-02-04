"""Sample API Client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import async_timeout
from aiohttp import (
    ClientConnectionError,
    ClientConnectorDNSError,
    ClientSSLError,
)
from pydantic import BaseModel

if TYPE_CHECKING:
    import aiohttp


API_PATH = "api/v1/"
CONFIG_PATH = urljoin(API_PATH, "config")
STATUSES_PATH = urljoin(API_PATH, "endpoints/statuses")


class GatusApiClientError(Exception):
    """Base Gatus API Client Exception."""


class GatusApiClientTimeoutError(GatusApiClientError):
    """Gatus API Client Timeout Exception."""


class GatusApiClientDNSError(GatusApiClientError):
    """Gatus API Client DNS Exception."""


class GatusApiClientConnectionError(GatusApiClientError):
    """Gatus API Client Connection Exception."""


class GatusApiClientSSLError(GatusApiClientError):
    """Gatus API Client SSL Exception."""


class ConfigResponse:
    """ConfigResponse is the response from the config endpoint in Gatus."""

    def __init__(self, data: dict) -> None:
        """Create an Instance of ConfigResponse."""
        self.oidc = data.get("oidc", False)
        self.authenticated = data.get("authenticated", False)


class GatusEndpointStatus(BaseModel):
    """Status is a single endpoint status in gatus."""

    name: str
    group: str
    key: str
    hostname: str
    last_checked: str
    success: bool
    response_time: int
    errors: list[str]

    @classmethod
    def from_dict(cls: type[GatusEndpointStatus], data: dict) -> GatusEndpointStatus:
        """Status is a single endpoint status in gatus."""
        last_check = data["results"][-1]

        return cls(
            name=data["name"],
            group=data.get("group", ""),
            key=data["key"],
            hostname=last_check["hostname"],
            last_checked=last_check["timestamp"],
            success=last_check["success"],
            response_time=last_check["duration"],
            errors=last_check.get("errors", []),
        )


class StatusesResponse(BaseModel):
    """StatusesResponse is a list of Statuses from the Gatus status endpoint."""

    statuses: list[GatusEndpointStatus]

    @classmethod
    def from_list(cls: type[StatusesResponse], data: list[dict]) -> StatusesResponse:
        """StatusesResponse is a list of Statuses from the Gatus status endpoint."""
        return cls(
            statuses=[GatusEndpointStatus.from_dict(endpoint) for endpoint in data]
        )


class GatusApiClient:
    """Sample API Client."""

    def __init__(
        self,
        url: str,
        session: aiohttp.ClientSession,
        verify_ssl: bool,  # noqa: FBT001
    ) -> None:
        """Initialize the API client."""
        self._url = url
        self._verify_ssl = verify_ssl
        self._session = session

    async def async_get_config(self) -> ConfigResponse:
        """Get the configuration."""
        data = await self._get(CONFIG_PATH)
        return ConfigResponse(data)

    async def async_get_statuses(self) -> StatusesResponse:
        """Get the statuses."""
        data = await self._get(STATUSES_PATH)
        return StatusesResponse.from_list(data)

    async def _get(self, path: str) -> Any:
        """Make a GET request."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(
                    urljoin(self._url, path), ssl=self._verify_ssl
                )
                response.raise_for_status()
                return await response.json()
        except TimeoutError as e:
            msg = f"Timeout error getting from {path}: {e}"
            raise GatusApiClientTimeoutError(msg) from e
        except ClientSSLError as e:
            msg = f"SSL error getting from {path}: {e}"
            raise GatusApiClientSSLError(msg) from e
        except ClientConnectorDNSError as e:
            msg = f"DNS error getting from {path}: {e}"
            raise GatusApiClientDNSError(msg) from e
        except ClientConnectionError as e:
            msg = f"Connection error getting from {path}: {e}"
            raise GatusApiClientConnectionError(msg) from e
        except Exception as e:
            msg = f"Error getting from {path}: {e}"
            raise GatusApiClientError(msg) from e
