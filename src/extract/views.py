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

"""Extract endpoint."""

from typing import List, Union

from fastapi import APIRouter, Depends, status, Query
from pydantic import Required

from src.logging_utils import Logger
from src.middlewares.authentication import check_api_key
from src.middlewares.exception_handling import HTTPException
from src.extract.models import ExtractedDoc, FailedExtraction
from src.extract.service import extract_pdf

router = APIRouter()
logger = Logger(name=__name__)


@router.post("",
             status_code=200,
             response_model=List[Union[ExtractedDoc, FailedExtraction]],
             dependencies=[Depends(check_api_key)])
def extract_view(
    path: List[str] = Query(default=Required)
):
    """Extract text from a PDF document.

    Args:
        path (:obj:`List[str]`):
            The path(s) of the documents to extract the text from. These are
            specified as query parameters, e.g.::

               /api/v1/extract/?path=123&path=456&path=789

            Passing only one path also works, e.g.::

               /api/v1/extract/?path=123

    Returns:
        :obj:`List[ExtractResponse]`: The extracted text.
    """
    try:
        return extract_pdf(path)
    except Exception as ex:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex
