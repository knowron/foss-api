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
from fastapi import HTTPException, status
from botocore.exceptions import BotoCoreError

from src.utils import s3_connection
from src.extract.models import ExtractedDoc, FailedExtraction, Page

import urllib.parse


def extract_single(path: str) -> Union[ExtractedDoc, FailedExtraction]:
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
        path = urllib.parse.unquote(path)
        doc = s3_connection.fetch_file(path)
    except HTTPException as ex:
        return FailedExtraction(
            path=path,
            status_code=ex.status_code,
            detail=ex.detail
        )
    except BotoCoreError as ex:
        ex_name: str = str(type(ex)).lstrip("<class '").rstrip("'>")
        return FailedExtraction(
            path=path,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(f"{ex_name}: {ex}")
        )

    try:
        with fitz.open(stream=doc,
                       filetype="application/pdf") as doc:
            doc_hash = hashlib.sha256(doc.stream).hexdigest()
            toc = doc.get_toc()
            if not toc:
                toc = None
            
            pages = []
            
            for number, page in enumerate(doc, 1):
                page_dict = page.get_text("dict")

                for block in page_dict["blocks"]:
                    if block["type"] == 0:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                try:
                                    span["text"] = span["text"].encode('utf8','surrogateescape')
                                except:
                                    span["text"] = " "

                pages.append(Page(
                    number=number,
                    width=page_dict["width"],
                    height=page_dict["height"],
                    blocks=page_dict["blocks"]
                )) 


        elapsed_seconds = time.perf_counter() - start_time
        return ExtractedDoc(
            path=path,
            hash=doc_hash,
            elapsed_seconds=elapsed_seconds,
            toc=toc,
            pages=pages
        )
    except RuntimeError as ex:
        return FailedExtraction(
            path=path,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(f"PyMuPDF couldn't process the doc: {ex}")
        )


def extract(paths: List[str]) -> List[Union[ExtractedDoc, FailedExtraction]]:
    """Extract contents from PDFs.

    Args:
        paths (:obj:`List[str]`):
            The path(s) of the documents to extract the text from.

    Returns:
        :obj:`List[Union[ExtractedDoc, FailedExtraction]]`: The extracted
        contents from the docs.
    """
    return [extract_single(path) for path in paths]
