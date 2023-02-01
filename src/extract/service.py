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

"""Services for the ``v1/extract`` endpoint."""

import hashlib
import time
from typing import List, Union

import fitz
from fastapi import HTTPException

from src.utils import s3_connection
from src.extract.models import ExtractedDoc, FailedExtraction, Page


def extract_pdf(paths: List[str]) -> List[Union[ExtractedDoc, FailedExtraction]]:
    """Extract contents from a PDF.

    Args:
        paths (:obj:`List[str]`):
            The path(s) of the documents to extract the text from.

    Returns:
        :obj:`List[Union[ExtractedDoc, FailedExtraction]]`: The extracted
        contents from the docs.
    """
    def extract(path: str) -> Union[ExtractedDoc, FailedExtraction]:
        """Extract a single PDF.

        Args:
            path (:obj:`str`):
                The path of the documents to extract the text from.

        Returns:
            :obj:`Union[ExtractedDoc, FailedExtraction]`: Th extracted contents
            from the doc.
        """
        start_time = time.perf_counter()
        try:
            doc = s3_connection.fetch_file(path)
        except HTTPException as ex:
            return FailedExtraction(
                path=path,
                status_code=ex.status_code,
                detail=ex.detail
            )
        with fitz.open(stream=doc,
                       filetype="application/pdf") as doc:
            doc_hash = hashlib.sha256(doc.stream).hexdigest()
            toc = doc.get_toc()
            if not toc:
                toc = None
            pages = [
                Page(
                    number=number,
                    width=page.get_text("dict")["width"],
                    height=page.get_text("dict")["height"],
                    blocks=[b for b in page.get_text("dict")["blocks"]]
                ) for number, page in enumerate(doc, 1)
            ]
        elapsed_seconds = time.perf_counter() - start_time
        return ExtractedDoc(
            path=path,
            hash=doc_hash,
            elapsed_seconds=elapsed_seconds,
            toc=toc,
            pages=pages
        )

    return [extract(path) for path in paths]
