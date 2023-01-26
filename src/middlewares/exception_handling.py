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

"""Exception handling utilities."""

from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException as FastApiHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.logging_utils import Logger, ErrorModel

logger = Logger(name=__name__)


class HTTPException(FastApiHTTPException):
    """Custom HTTP Exception that includes the attribute :attr:`body`.

    This exception must be re-raised by all our endpoints upon an error. It will
    then be appropriately handled by our :func:`global_exception_handler`.

    Attributes:
        status_code(:obj:`int`):
            The HTTP status code of the exception.
        detail (:obj:`Optional[Any]`):
            The HTTP status code of the exception.
        headers (:obj:`Optional[Dict[str, Any]]`, defaults to `None`):
            The HTTP status code of the exception.
        body (:obj:`Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]`):
            The body of the request that caused the exception, if any.
    """
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    ) -> None:
        self.body = body if body else {}
        super().__init__(status_code=status_code, detail=detail, headers=headers)

    def __str__(self) -> str:
        return self.detail


async def global_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Global exception handler.

    This handler homogenizes the response and logging upon any raised exception
    derived from a call to any of our endpoints.

    Args:
        request (:obj:`fastapi.Request`):
            The request that caused the error.
        exc (:obj:`HTTPException`):
            The HTTP exception raised.

            .. note::

               All endpoints must catch global :obj:`Exception`s and re-raise
               them as :obj:`HTTPException`s! This way we can keep the body
               of the failed request.

    Returns:
        :obj:`fastapi.responses.JSONResponse`: A FastAPI JSON response that
        wraps our :class:`src.logging_utils.ErrorModel`, common to all errors.
    """
    if isinstance(exc, RequestValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif hasattr(exc, "status_code"):
        status_code = exc.status_code
    else:
        status.HTTP_500_INTERNAL_SERVER_ERROR
    body = exc.body if hasattr(exc, "body") else {},
    headers = dict(request.headers) if request.headers else {}
    if headers and "authorization" in headers:
        # Don't return the API key (although if you made it this far you
        # probably already have it anyways).
        headers["authorization"] = "*****"
    error: ErrorModel = logger.generate_error(
        api_route=request.url.path,
        query_params=request.query_params,
        headers=headers,
        request_body=body,
        status_code=status_code,
        exception=exc
    )
    # Log the exception before returning.
    logger.exception(exception=exc, info=error)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(error.dict())
    )


# Global exception handlers used by our API.
# See https://www.starlette.io/exceptions/
exception_handlers: Dict[Union[int, Exception],
                         Callable[[Request, Exception], Response]] = {
    RequestValidationError: global_exception_handler,
    HTTPException: global_exception_handler
}
