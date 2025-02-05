"""Test the Gatus config flow."""

from collections.abc import Callable, Generator
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_mock import MockerFixture

from custom_components.gatus.api import (
    GatusApiClientConnectionError,
    GatusApiClientDNSError,
    GatusApiClientError,
    GatusApiClientSSLError,
    GatusApiClientTimeoutError,
)


@pytest.fixture
def mock_setup_entry() -> Generator[None, None, None]:
    with patch("custom_components.gatus.async_setup_entry", return_value=True) as mock:
        yield mock


async def test_show_form(hass: HomeAssistant) -> None:
    """Test that the form is served with no input."""
    result = await hass.config_entries.flow.async_init(
        "gatus", context={"source": config_entries.SOURCE_USER}
    )

    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}


async def test_create_entry(
    hass: HomeAssistant,
    mocked_client: MockerFixture,
    mocker: Callable[..., Generator[MockerFixture, None, None]],
) -> None:
    """Test creating an entry."""
    mocker.patch.object(mocked_client, "async_get_statuses", return_value={})

    result = await hass.config_entries.flow.async_init(
        "gatus",
        context={"source": config_entries.SOURCE_USER},
        data={
            CONF_NAME: "Test Monitor",
            CONF_URL: "http://example.com",
            CONF_VERIFY_SSL: True,
        },
    )
    assert result.get("type") == FlowResultType.CREATE_ENTRY
    assert result.get("title") == "Test Monitor"
    assert result.get("data") == {
        CONF_NAME: "Test Monitor",
        CONF_URL: "http://example.com",
        CONF_VERIFY_SSL: True,
    }


@pytest.mark.parametrize(
    ("exception", "error_key"),
    [
        (GatusApiClientTimeoutError, "timeout"),
        (GatusApiClientSSLError, "ssl"),
        (GatusApiClientDNSError, "dns"),
        (GatusApiClientConnectionError, "connection"),
        (GatusApiClientError, "unknown"),
    ],
)
async def test_handle_exception(
    hass: HomeAssistant,
    mocked_client: None,
    mocker: Callable[..., Generator[MockerFixture, None, None]],
    exception: Exception,
    error_key: str,
) -> None:
    """Test handling a timeout error."""
    mocker.patch.object(
        mocked_client,
        "async_get_statuses",
        mocker.AsyncMock(side_effect=exception),
    )

    result = await hass.config_entries.flow.async_init(
        "gatus",
        context={"source": config_entries.SOURCE_USER},
        data={
            CONF_NAME: "Test Monitor",
            CONF_URL: "http://example.com",
            CONF_VERIFY_SSL: True,
        },
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {"base": error_key}
