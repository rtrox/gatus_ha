"""Tests for the Gatus API client."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import Mock

import pytest
from aiohttp import (
    ClientConnectionError,
    ClientConnectorDNSError,
    ClientSession,
    ClientSSLError,
)
from aioresponses import aioresponses

from custom_components.gatus_ha.api import (
    ConfigResponse,
    GatusApiClient,
    GatusApiClientConnectionError,
    GatusApiClientDNSError,
    GatusApiClientSSLError,
    GatusApiClientTimeoutError,
    StatusesResponse,
)

API_URL = "http://testserver/"
CONFIG_PATH = "api/v1/config"
STATUSES_PATH = "api/v1/endpoints/statuses"


@pytest.fixture
async def client() -> AsyncGenerator[GatusApiClient, Any]:
    async with ClientSession() as session:
        yield GatusApiClient(API_URL, session, verify_ssl=False)


@pytest.mark.asyncio
async def test_async_get_config(client: GatusApiClient) -> None:
    with aioresponses() as m:
        m.get(f"{API_URL}{CONFIG_PATH}", payload={"oidc": True, "authenticated": True})

        response = await client.async_get_config()
        assert isinstance(response, ConfigResponse)
        assert response.oidc is True
        assert response.authenticated is True


@pytest.mark.asyncio
async def test_async_get_statuses(client: GatusApiClient) -> None:
    with aioresponses() as m:
        m.get(
            f"{API_URL}{STATUSES_PATH}",
            payload=[
                {
                    "name": "test",
                    "key": "test-key",
                    "results": [
                        {
                            "hostname": "test-host",
                            "timestamp": "2023-01-01T00:00:00Z",
                            "success": True,
                            "duration": 100,
                            "errors": [],
                        }
                    ],
                }
            ],
        )

        response = await client.async_get_statuses()
        assert isinstance(response, StatusesResponse)
        assert len(response.statuses) == 1
        assert response.statuses[0].name == "test"
        assert response.statuses[0].success is True


@pytest.mark.asyncio
async def test_timeout_error(client: GatusApiClient) -> None:
    with aioresponses() as m:
        m.get(f"{API_URL}{CONFIG_PATH}", exception=TimeoutError)

        with pytest.raises(GatusApiClientTimeoutError):
            await client.async_get_config()


@pytest.mark.asyncio
async def test_ssl_error(client: GatusApiClient) -> None:
    connection_key = Mock()
    os_error = OSError("SSL error")
    with aioresponses() as m:
        m.get(
            f"{API_URL}{CONFIG_PATH}",
            exception=ClientSSLError(connection_key, os_error),
        )

        with pytest.raises(GatusApiClientSSLError):
            await client.async_get_config()


@pytest.mark.asyncio
async def test_dns_error(client: GatusApiClient) -> None:
    connection_key = Mock()
    os_error = OSError("DNS error")
    with aioresponses() as m:
        m.get(
            f"{API_URL}{CONFIG_PATH}",
            exception=ClientConnectorDNSError(connection_key, os_error),
        )

        with pytest.raises(GatusApiClientDNSError):
            await client.async_get_config()


@pytest.mark.asyncio
async def test_connection_error(client: GatusApiClient) -> None:
    with aioresponses() as m:
        m.get(f"{API_URL}{CONFIG_PATH}", exception=ClientConnectionError)

        with pytest.raises(GatusApiClientConnectionError):
            await client.async_get_config()
