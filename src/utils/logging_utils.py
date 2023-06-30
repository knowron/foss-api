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

"""Logging utilities."""

import logging
import traceback
from datetime import datetime, timezone
from typing import Optional

from config import settings, ENV
from .models import ErrorModel, OriginatingSystem


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
        path: str,
        status_code: int,
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
            traceback_ = traceback.format_exc()
        else:
            message = None
            traceback_ = None

        return ErrorModel(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            originating_system=OriginatingSystem.FOSS_API,
            environment=ENV,
            log_level=logging.getLevelName(self._log_level),
            path=path,
            status_code=status_code,
            message=message,
            stack_trace=traceback_
        )
