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

"""Models for document extraction."""

from enum import Enum

from pydantic import validator

from config import Environment, ENV
from utils.base_model import CamelModel


class OriginatingSystem(Enum):
    """The system in which the error occurred.

    Attributes:
        FOSS_API:
            The FOSS API.
    """

    FOSS_API = "foss-api"


class ErrorModel(CamelModel):
    """Response model for errored documents.

    Attributes:
        success (:obj:`bool`):
            Whether the extraction succeeded. Always set to ``False``.
        timestamp (:obj:`str`):
            The time when the error happened.
        originating_system (:obj:`str`, `optional`):
            The system that generated the log.
        environment (:obj:`src.config.Environment`, `optional`):
            The environment in which the error occurred, e.g., "staging".
        path (:obj:`str`):
            The path of the document that could not be extracted.
        status_code (:obj:`int`):
            The status code of the error, e.g., ``500``.
        message (:obj:`str | None`):
            The error message (if any).
        stack_trace (:obj:`str | None`):
            The stack trace (if errors have happened).
    """

    success: bool = False
    timestamp: str
    originating_system: OriginatingSystem = OriginatingSystem.FOSS_API
    environment: Environment = ENV
    log_level: str
    path: str
    status_code: int
    message: str | None
    stack_trace: str | None

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


class Success(CamelModel):
    """Response model when the extraction was successful.

    Attributes:
        success (:obj:`bool`):
            Whether the extraction succeeded. Always set to ``True``.
        doc_hash (:obj:`str`):
            The hash of the document binary.
        key (:obj:`str | None`):
            The S3 key to the extracted contents. If :obj:`None`, the document
            is image-based.
        doc_type (:obj:`str`):
            The type of the document. Must be one of the values defined in
            :class:`utils.document_types.DocType`.
    """
    success: bool = True
    doc_hash: str
    key: str | None
    doc_type: str
