"""DataUpdateCoordinator for gatus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    GatusApiClient,
    GatusApiClientError,
    StatusesResponse,
)
from .const import COORDINATOR_UPDATE_INTERVAL, DOMAIN, LOGGER

if TYPE_CHECKING:  # pragma: no cover
    from homeassistant.core import HomeAssistant

    from .data import GatusConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class GatusDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    data: StatusesResponse
    config_entry: GatusConfigEntry
    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry_id: str,
        client: GatusApiClient,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=COORDINATOR_UPDATE_INTERVAL,
        )
        self._config_entry_id = config_entry_id
        self.client = client

    async def _async_update_data(self) -> StatusesResponse:
        """Update data via library."""
        try:
            response = await self.client.async_get_statuses()
        except GatusApiClientError as exception:
            raise UpdateFailed(exception) from exception

        return response
