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

"""Logging utilities for all endpoints."""

import sys
import logging
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import validator
from src.base_model import CamelModel
from src.config import settings, Environment, ENV


class OriginatingSystem(Enum):
    """The system in which the error occurred.

    Attributes:
        FOSS_API:
            The FOSS API.
    """

    FOSS_API = "foss-api"


class ErrorModel(CamelModel):
    """Error model for all endpoints.

    This is the schema that all endpoints will return when any error happens.

    Attributes:
        timestamp (:obj:`str`):
            The time when the error happened.
        originating_system (:obj:`str`, `optional`):
            The system that generated the log.
        environment (:obj:`src.config.Environment`, `optional`):
            The environment in which the error occurred, e.g., "staging".
        log_level (:obj:`str`):
            The level of the log, e.g., "warning".
        api_route (:obj:`str`):
            The API endpoint the request was made to.
        headers (:obj:`Dict[str, Any]`, `optional`):
            The headers of the request.
        query_params (:obj:`Dict[str, Any]`, `optional`):
            The query parameters of the request.
        request_body (:obj:`Union[dict, list]`, `optional`):
            The body of the request.
        status_code (:obj:`int`):
            The status code of the error, e.g., ``500``.
        message (:obj:`Optional[str]`):
            The error message (if any).
        stack_trace (:obj:`Optional[str]`):
            The stack trace (if errors have happened).
    """

    timestamp: str
    originating_system: OriginatingSystem = OriginatingSystem.FOSS_API
    environment: Environment = ENV
    log_level: str
    api_route: str
    query_params: Dict[str, Any] = {}
    headers: Dict[str, Any] = {}
    request_body: Union[dict, list] = {}
    status_code: int
    message: Optional[str]
    stack_trace: Optional[str]

    @validator("message")
    def set_default_message(cls, message):
        """Set a default message if needed.

        The default value is set when the passed message is empty or
        :obj:`None`.
        """
        return message or "no message available"

    @validator("stack_trace")
    def set_default_stack_trace(cls, stack_trace):
        """Set a default stack trace if needed.

        The default value is set when the passed stack trace is empty or
        :obj:`None`.
        """
        return stack_trace or "no stack trace available"

    class Config:
        validate_assignment = True
        use_enum_values = True


class Logger:
    """API Logger.

    Attributes:
        name (:obj:`str`):
            The name of the logger.
        _log_level (:obj:`Optional[int]`):
            The logging level, e.g. :obj:`logging.WARNING`.
        _logger (:obj:`logging.Logger`):
            The logger used internally by this class.
    """

    def __init__(self, name: str, log_level: Optional[int] = None):
        self.name = name
        if log_level is None:
            log_level = settings.get_log_level()
        self._log_level = log_level
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self._log_level)

    @property
    def log_level(self):
        return self._log_level

    def debug(self, msg: str, *args, **kwargs):
        """Log a message with level DEBUG.

        See `https://docs.python.org/3/library/logging.html#logging.Logger.debug`__.
        """
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log a message with level INFO.

        See `https://docs.python.org/3/library/logging.html#logging.Logger.info`__.
        """
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log a message with level WARNING.

        See `https://docs.python.org/3/library/logging.html#logging.Logger.warning`__.
        """
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log a message with level ERROR.

        See `https://docs.python.org/3/library/logging.html#logging.Logger.error`__.
        """
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log a message with level CRITICAL.

        See `https://docs.python.org/3/library/logging.html#logging.Logger.critical`__.
        """
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, exception: Exception, info: ErrorModel):
        """Log exception.

        Args:
            exception (:obj:`Exception`):
                The exception to be logged.
            info (:obj:`ErrorModel`):
                The information about the exception.
        """
        extra = info.dict(exclude={"message"})  # message already passed in "msg"
        self._logger.exception(
            msg=info.message,
            exc_info=exception,
            extra=extra
        )

    def generate_error(
        self,
        api_route: str,
        status_code: int,
        headers: Dict[str, Any] = {},
        query_params: Dict[str, Any] = {},
        request_body: Union[dict, list, CamelModel] = {},
        exception: Optional[Exception] = None
    ) -> ErrorModel:
        """Compile an :obj:`ErrorModel`.

        This method takes care of the initialization of certain fields in an
        :obj:`ErrorModel`, such as the :attr:`timestamp` (current time will be
        set), :attr:`originating_system` and :attr:`environment`.

        See :class:`ErrorModel` for info about the arguments.
        """
        if exception:
            message = str(exception)
            # TODO: In Python 3.10 traceback.format_exception() has changed!
            # See https://docs.python.org/3/library/traceback.html#traceback.format_exception
            traceback_ = "".join(traceback.format_exception(*sys.exc_info()))
        else:
            message = None
            traceback_ = None

        return ErrorModel(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            originating_system=OriginatingSystem.FOSS_API,
            environment=ENV,
            log_level=logging.getLevelName(self._log_level),
            api_route=api_route,
            headers=headers,
            query_params=query_params,
            request_body=request_body.dict(
                exclude_unset=True,
                by_alias=True
            ) if isinstance(request_body, CamelModel) else request_body,
            status_code=status_code,
            message=message,
            stack_trace=traceback_
        )
