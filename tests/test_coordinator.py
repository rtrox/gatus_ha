"""Test the Gatus coordinator."""

from collections.abc import Callable, Generator

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_mock import MockerFixture

from custom_components.gatus.api import (
    GatusApiClient,
    GatusApiClientError,
    GatusApiClientTimeoutError,
    StatusesResponse,
)
from custom_components.gatus.coordinator import GatusDataUpdateCoordinator


@pytest.fixture
def coordinator(mocked_entry: tuple) -> GatusDataUpdateCoordinator:
    hass, entry, client = mocked_entry
    return GatusDataUpdateCoordinator(
        hass=hass,
        config_entry_id="test_entry_id",
        client=client,
    )


@pytest.mark.asyncio
async def test_async_update_data_success(
    coordinator: GatusDataUpdateCoordinator,
    mocked_client: GatusApiClient,
    mocker: Callable[..., Generator[MockerFixture, None, None]],
) -> None:
    mocker.patch.object(
        mocked_client,
        "async_get_statuses",
        mocker.AsyncMock(return_value=StatusesResponse(statuses=[])),
    )
    result = await coordinator._async_update_data()

    assert isinstance(result, StatusesResponse)
    assert result.statuses == []


@pytest.mark.asyncio
async def test_async_update_data_timeout_error(
    coordinator: GatusDataUpdateCoordinator, mocked_client: GatusApiClient
) -> None:
    mocked_client.async_get_statuses.side_effect = GatusApiClientTimeoutError

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_async_update_data_client_error(
    coordinator: GatusDataUpdateCoordinator, mocked_client: GatusApiClient
) -> None:
    mocked_client.async_get_statuses.side_effect = GatusApiClientError

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
