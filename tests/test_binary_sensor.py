"""Tests for the Gatus HA binary sensor integration."""

from typing import Any

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_mock import MockerFixture

from custom_components.gatus.api import (
    GatusEndpointStatus,
    StatusesResponse,
)


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
    mocker: MockerFixture,
) -> None:
    hass, entry, client = mocked_entry
    mocker.patch.object(
        client, "async_get_statuses", mocker.AsyncMock(return_value=statuses)
    )
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
    mocker: MockerFixture,
) -> None:
    hass, entry, client = mocked_entry
    mocker.patch.object(
        client, "async_get_statuses", mocker.AsyncMock(return_value=statuses)
    )
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_reg = er.async_get(hass)
    for entity in expected_entities:
        assert entity_reg.async_get(entity) is not None
        state = hass.states.get(entity)
        assert state
        assert state.state == is_on
