"""BlueprintEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import GatusDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription

    from .api import GatusEndpointStatus


class GatusEntity(CoordinatorEntity[GatusDataUpdateCoordinator]):
    """BlueprintEntity class."""

    def __init__(
        self,
        coordinator: GatusDataUpdateCoordinator,
        description: EntityDescription,
        status: GatusEndpointStatus,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._status = status
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{status.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            manufacturer="Gatus Integration",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_extra_state_attributes = {
            "name": status.name,
            "group": status.group,
            "key": status.key,
            "hostname": status.hostname,
            "last_checked": status.last_checked,
            "response_time": status.response_time,
            "errors": status.errors,
            "url": f"{coordinator.config_entry.data['url']}/endpoints/{status.key}",
        }
        self.entity_description = description
        self._endpoint_status = status
        self._api = coordinator.client
