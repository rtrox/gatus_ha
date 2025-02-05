"""Unit tests for the GatusEntity class in the gatus integration."""

from unittest.mock import MagicMock

import pytest
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from custom_components.gatus.coordinator import GatusDataUpdateCoordinator
from custom_components.gatus.entity import GatusEntity


@pytest.fixture
def setup() -> tuple[GatusDataUpdateCoordinator, MagicMock, MagicMock]:
    coordinator = MagicMock(spec=GatusDataUpdateCoordinator)
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.domain = "test_domain"
    config_entry.data = {"url": "http://test-url"}
    coordinator.config_entry = config_entry
    coordinator.client = MagicMock()

    description = MagicMock()
    status = MagicMock()
    status.key = "test_key"
    status.name = "test_name"
    status.group = "test_group"
    status.hostname = "test_hostname"
    status.last_checked = "test_last_checked"
    status.response_time = "test_response_time"
    status.errors = "test_errors"

    return coordinator, description, status


def test_init(setup: tuple[GatusDataUpdateCoordinator, MagicMock, MagicMock]) -> None:
    coordinator, description, status = setup
    entity = GatusEntity(coordinator, description, status)

    assert entity._status == status
    assert entity._attr_unique_id == "test_entry_id_test_key"
    assert entity._attr_device_info == DeviceInfo(
        identifiers={("test_domain", "test_entry_id")},
        manufacturer="Gatus Integration",
        entry_type=DeviceEntryType.SERVICE,
    )
    assert entity._attr_extra_state_attributes == {
        "name": "test_name",
        "group": "test_group",
        "key": "test_key",
        "hostname": "test_hostname",
        "last_checked": "test_last_checked",
        "response_time": "test_response_time",
        "errors": "test_errors",
        "url": "http://test-url/endpoints/test_key",
    }
    assert entity.entity_description == description
    assert entity._endpoint_status == status
    assert entity._api == coordinator.client
