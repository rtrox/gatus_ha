"""Constants for integration_blueprint."""

from datetime import timedelta
from logging import Logger, getLogger

DOMAIN = "gatus"
COORDINATOR_UPDATE_INTERVAL = timedelta(seconds=10)

LOGGER: Logger = getLogger(__package__)
