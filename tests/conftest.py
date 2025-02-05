"""Fixtures for testing."""

from collections.abc import Callable, Generator
from typing import Any

import pytest
from homeassistant.const import CONF_NAME, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_mock import MockerFixture

from custom_components.gatus.api import GatusApiClient
from custom_components.gatus.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: Any,
) -> None:
    """Enable custom integrations."""


@pytest.fixture
async def mocked_client(
    mocker: Callable[..., Generator[MockerFixture, None, None]],
) -> None:
    client = mocker.MagicMock(spec=GatusApiClient)
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
