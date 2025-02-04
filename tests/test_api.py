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
    GatusEndpointStatus,
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


testdata = [
    pytest.param(
        [
            {
                "name": "atuin",
                "group": "apps",
                "key": "apps_atuin",
                "results": [
                    {
                        "status": 200,
                        "hostname": "atuin.example.com",
                        "duration": 43782513,
                        "conditionResults": [
                            {"condition": "[STATUS] == 200", "success": True}
                        ],
                        "success": True,
                        "timestamp": "2025-02-04T04:14:22.868295096Z",
                    },
                ],
            },
        ],
        StatusesResponse(
            statuses=[
                GatusEndpointStatus(
                    name="atuin",
                    group="apps",
                    key="apps_atuin",
                    hostname="atuin.example.com",
                    last_checked="2025-02-04T04:14:22.868295096Z",
                    success=True,
                    response_time=43782513,
                    errors=[],
                )
            ]
        ),
        id="single_status",
    ),
    pytest.param(
        [
            {
                "name": "atuin",
                "group": "apps",
                "key": "apps_atuin",
                "results": [
                    {
                        "status": 200,
                        "hostname": "atuin.example.com",
                        "duration": 43782513,
                        "conditionResults": [
                            {"condition": "[STATUS] == 200", "success": True}
                        ],
                        "success": True,
                        "timestamp": "2025-02-04T04:14:22.868295096Z",
                    },
                    {
                        "hostname": "atuin.example.com",
                        "duration": 84588472,
                        "errors": [
                            'Get "https://atuin.example.com": dial tcp: lookup link.rtrox.io on 1.1.1.1:53: no such host'  # noqa: E501
                        ],
                        "conditionResults": [
                            {"condition": "[STATUS] (0) == 200", "success": False}
                        ],
                        "success": False,
                        "timestamp": "2025-02-04T04:14:33.22021085Z",
                    },
                ],
            },
        ],
        StatusesResponse(
            statuses=[
                GatusEndpointStatus(
                    name="atuin",
                    group="apps",
                    key="apps_atuin",
                    hostname="atuin.example.com",
                    last_checked="2025-02-04T04:14:33.22021085Z",
                    success=False,
                    response_time=84588472,
                    errors=[
                        'Get "https://atuin.example.com": dial tcp: lookup link.rtrox.io on 1.1.1.1:53: no such host'  # noqa: E501
                    ],
                )
            ]
        ),
        id="use_last_status_with_errors",
    ),
    pytest.param(
        [
            {
                "name": "atuin",
                "key": "atuin",
                "results": [
                    {
                        "status": 200,
                        "hostname": "atuin.example.com",
                        "duration": 43782513,
                        "conditionResults": [
                            {"condition": "[STATUS] == 200", "success": True}
                        ],
                        "success": True,
                        "timestamp": "2025-02-04T04:14:22.868295096Z",
                    },
                ],
            },
        ],
        StatusesResponse(
            statuses=[
                GatusEndpointStatus(
                    name="atuin",
                    group="",
                    key="atuin",
                    hostname="atuin.example.com",
                    last_checked="2025-02-04T04:14:22.868295096Z",
                    success=True,
                    response_time=43782513,
                    errors=[],
                )
            ]
        ),
        id="single_status_no_group",
    ),
    pytest.param(
        [
            {
                "name": "atuin",
                "key": "atuin",
                "results": [
                    {
                        "status": 200,
                        "hostname": "atuin.example.com",
                        "duration": 43782513,
                        "conditionResults": [
                            {"condition": "[STATUS] == 200", "success": True}
                        ],
                        "success": True,
                        "timestamp": "2025-02-04T04:14:22.868295096Z",
                    },
                ],
            },
            {
                "name": "shlink",
                "group": "apps",
                "key": "apps_shlink",
                "results": [
                    {
                        "hostname": "link.rtrox.io",
                        "duration": 84588472,
                        "errors": [
                            'Get "https://link.rtrox.io": dial tcp: lookup link.rtrox.io on 10.96.0.10:53: no such host'  # noqa: E501
                        ],
                        "conditionResults": [
                            {"condition": "[STATUS] (0) == 200", "success": False}
                        ],
                        "success": False,
                        "timestamp": "2025-02-04T04:14:33.22021085Z",
                    }
                ],
            },
        ],
        StatusesResponse(
            statuses=[
                GatusEndpointStatus(
                    name="atuin",
                    group="",
                    key="atuin",
                    hostname="atuin.example.com",
                    last_checked="2025-02-04T04:14:22.868295096Z",
                    success=True,
                    response_time=43782513,
                    errors=[],
                ),
                GatusEndpointStatus(
                    name="shlink",
                    group="apps",
                    key="apps_shlink",
                    hostname="link.rtrox.io",
                    last_checked="2025-02-04T04:14:33.22021085Z",
                    success=False,
                    response_time=84588472,
                    errors=[
                        'Get "https://link.rtrox.io": dial tcp: lookup link.rtrox.io on 10.96.0.10:53: no such host'  # noqa: E501
                    ],
                ),
            ]
        ),
        id="multiple_statuses",
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("statuses", "expected"), testdata)
async def test_async_get_statuses(
    client: GatusApiClient, statuses: dict, expected: StatusesResponse
) -> None:
    with aioresponses() as m:
        m.get(
            f"{API_URL}{STATUSES_PATH}",
            payload=statuses,
        )

        response = await client.async_get_statuses()
        assert isinstance(response, StatusesResponse)
        assert response == expected


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
