"""The Gatus Home Assistant integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_URL, CONF_VERIFY_SSL, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import GatusApiClient
from .const import LOGGER
from .coordinator import GatusDataUpdateCoordinator
from .data import GatusData

if TYPE_CHECKING:  # pragma: no cover
    from homeassistant.core import HomeAssistant

    from .data import GatusConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GatusConfigEntry,
) -> bool:
    """Set up the Gatus integration."""
    coordinator = GatusDataUpdateCoordinator(
        hass=hass,
        config_entry_id=entry.entry_id,
        client=GatusApiClient(
            url=entry.data[CONF_URL],
            session=async_get_clientsession(hass),
            verify_ssl=entry.data[CONF_VERIFY_SSL],
        ),
    )
    entry.runtime_data = GatusData(
        client=GatusApiClient(
            url=entry.data[CONF_URL],
            session=async_get_clientsession(hass),
            verify_ssl=entry.data[CONF_VERIFY_SSL],
        ),
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    LOGGER.info("Integration %s has been set up", entry.title)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: GatusConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: GatusConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
