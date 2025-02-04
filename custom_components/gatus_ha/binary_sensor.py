"""Binary sensor platform for gatus_ha."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import GatusEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import GatusEndpointStatus
    from .coordinator import GatusDataUpdateCoordinator
    from .data import GatusConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="gatus",
        name="Gatus Endpoint is Up",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: GatusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        GatusBinarySensor(
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=endpoint.key,
                name=endpoint.name,
                device_class=BinarySensorDeviceClass.CONNECTIVITY,
            ),
            status=endpoint,
        )
        for endpoint in coordinator.data.statuses
    )


class GatusBinarySensor(GatusEntity, BinarySensorEntity):
    """Gatus binary_sensor class."""

    def __init__(
        self,
        coordinator: GatusDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        status: GatusEndpointStatus,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description, status)
        self.entity_description = entity_description
        self.entity_id = f"binary_sensor.gatus_{status.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self._status.success
