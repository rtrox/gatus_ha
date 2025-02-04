"""Fixtures for testing."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: bool,  # noqa: FBT001
) -> None:
    """Enable custom integrations."""
