"""Tests for the Gatus HA binary sensor integration."""

from collections.abc import Callable, Generator
from typing import Any

import pytest
from homeassistant.const import CONF_NAME, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_mock.plugin import MockerFixture

from custom_components.gatus.api import (
    GatusApiClient,
    GatusEndpointStatus,
    StatusesResponse,
)
from custom_components.gatus.const import DOMAIN


@pytest.fixture
async def mocked_client(
    mocker: Callable[..., Generator[MockerFixture, None, None]],
    statuses: StatusesResponse,
) -> None:
    client = mocker.MagicMock(spec=GatusApiClient)
    mocker.patch.object(
        client, "async_get_statuses", mocker.AsyncMock(return_value=statuses)
    )
    mocker.patch.object(GatusApiClient, "__new__", return_value=client)
    return client


@pytest.fixture
async def mocked_entry(
    hass: HomeAssistant,
    mocked_client: Any,
    mocker: Callable[..., Generator[MockerFixture, None, None]],
) -> tuple[HomeAssistant, MockConfigEntry, Any]:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Test Gatus",
            CONF_URL: "http://localhost:8080",
            CONF_VERIFY_SSL: False,
        },
    )
    entry.add_to_hass(hass)
    return hass, entry, mocked_client


@pytest.fixture
async def mocked_entity(
    mocked_entry: tuple[Any, MockConfigEntry, Any],
) -> tuple[HomeAssistant, MockConfigEntry, Any]:
    hass, entry, client = mocked_entry
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return hass, entry, client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("statuses", "expected_entities"),
    [
        (
            StatusesResponse(
                statuses=[
                    GatusEndpointStatus(
                        key="apps_atuin",
                        name="atuin",
                        group="apps",
                        hostname="atuin.sh",
                        success=True,
                        last_checked="2023-10-01T00:00:00Z",
                        response_time=100,
                        errors=[],
                    ),
                    GatusEndpointStatus(
                        key="atuin",
                        name="atuin",
                        group="",
                        hostname="atuin.sh",
                        success=True,
                        last_checked="2023-10-01T00:00:00Z",
                        response_time=100,
                        errors=[],
                    ),
                    GatusEndpointStatus(
                        key="links_shlink",
                        group="links",
                        name="shlink",
                        hostname="shlink.local",
                        success=True,
                        last_checked="2023-10-01T00:00:00Z",
                        response_time=100,
                        errors=[],
                    ),
                ]
            ),
            [
                "binary_sensor.gatus_apps_atuin",
                "binary_sensor.gatus_atuin",
                "binary_sensor.gatus_links_shlink",
            ],
        ),
    ],
)
async def test_async_setup_entry(
    statuses: StatusesResponse,
    expected_entities: list[str],
    mocked_entry: tuple[Any, MockConfigEntry, Any],
) -> None:
    hass, entry, client = mocked_entry
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_reg = er.async_get(hass)
    for entity in expected_entities:
        assert entity_reg.async_get(entity) is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("statuses", "expected_entities", "is_on"),
    [
        (
            StatusesResponse(
                statuses=[
                    GatusEndpointStatus(
                        key="apps_atuin",
                        name="atuin",
                        group="apps",
                        hostname="atuin.sh",
                        success=True,
                        last_checked="2023-10-01T00:00:00Z",
                        response_time=100,
                        errors=[],
                    ),
                ]
            ),
            [
                "binary_sensor.gatus_apps_atuin",
            ],
            "on",
        ),
        (
            StatusesResponse(
                statuses=[
                    GatusEndpointStatus(
                        key="apps_atuin",
                        name="atuin",
                        group="apps",
                        hostname="atuin.sh",
                        success=False,
                        last_checked="2023-10-01T00:00:00Z",
                        response_time=100,
                        errors=[],
                    ),
                ]
            ),
            [
                "binary_sensor.gatus_apps_atuin",
            ],
            "off",
        ),
    ],
)
async def test_async_setup_entry_states(
    statuses: StatusesResponse,
    expected_entities: list[str],
    is_on: str,
    mocked_entry: tuple[Any, MockConfigEntry, Any],
) -> None:
    hass, entry, client = mocked_entry
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_reg = er.async_get(hass)
    for entity in expected_entities:
        assert entity_reg.async_get(entity) is not None
        state = hass.states.get(entity)
        assert state
        assert state.state == is_on
