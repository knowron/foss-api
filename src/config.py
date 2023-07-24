# Copyright (C) 2023 KNOWRON GmbH <ask@knowron.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For license information on the libraries used, see LICENSE.

"""API Configuration."""

import os
import logging
import warnings
from enum import Enum

from pydantic_settings import BaseSettings


class Environment(Enum):
    """Environment the API is being run on.

    Log level for each environment can be changed in
    :meth:`Settings.get_log_level`.
    """

    LOCAL = "local"
    STAGING = "staging"
    PROD = "prod"

    @classmethod
    def is_valid(cls, env: str) -> bool:
        """Determine whether a string represents a valid environment.

        Args:
            env (:obj:`str`):
                The environment to check support for.

        Returns:
            :obj:`bool`: Whether the string represents a valid environment or
            not.
        """
        return env in cls._value2member_map_


# We keep this variable out of `Settings` because we need to reference it from
# the settings themselves.
# We check if the environment variable "ENV" is defined and is a valid string,
# if not we default to Environment.STAGING.
ENV: Environment = (Environment(os.environ["ENV"])
                    if Environment.is_valid(os.environ.get("ENV"))
                    else Environment.STAGING)


class Settings(BaseSettings):
    """Settings."""

    EXTRACTION_VERSION: str = "1.0"

    #######
    # AWS #
    #######
    # Set variables below as Environment Variables from the AWS Console.
    AWS_REGION_NAME: str
    AWS_S3_ACCESS_KEY_ID: str
    AWS_S3_SECRET_ACCESS_KEY: str
    # The bucket storing the PDF documents.
    DOCS_S3_BUCKET_NAME: str
    # The bucket storing the extracted contents of the PDF docs.
    EXTRACTED_S3_BUCKET_NAME: str

    @classmethod
    def get_log_level(cls):
        """Return the log according to the current Environment."""
        if ENV in (Environment.LOCAL, Environment.STAGING):
            return logging.DEBUG
        else:
            return logging.INFO

    class Config:
        case_sensitive = True


settings = Settings()

# Disable logging globally for all logs under current log level.
# See https://docs.python.org/3/howto/logging.html#logging-levels
current_log_level = settings.get_log_level()
previous_log_level = (current_log_level - 10
                      if current_log_level != 0
                      else current_log_level)
logging.disable(previous_log_level)

# Disable warnings as well if current level > logging.WARNING
if current_log_level > logging.WARNING:
    warnings.filterwarnings("ignore")
