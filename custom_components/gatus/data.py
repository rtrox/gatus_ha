"""Custom types for gatus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:  # pragma: no cover
    from homeassistant.loader import Integration

    from .api import GatusApiClient
    from .coordinator import GatusDataUpdateCoordinator


type GatusConfigEntry = ConfigEntry[GatusData]


@dataclass
class GatusData:
    """Data for the Blueprint integration."""

    client: GatusApiClient
    coordinator: GatusDataUpdateCoordinator
    integration: Integration
