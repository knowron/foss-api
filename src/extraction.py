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

"""Lambda function for document extraction.

See the `AWS Lambda docs
<https://docs.aws.amazon.com/lambda/latest/dg/welcome.html>`_.
"""

import hashlib
import time
import urllib.parse
from typing import Union

import fitz
from botocore.exceptions import BotoCoreError

from utils import s3_connection
from utils.logging_utils import Logger, ErrorModel
from utils.models import ExtractedDoc


logger = Logger(name=__name__)


def extract(path: str) -> Union[ExtractedDoc, ErrorModel]:
    """Extract the text of a PDF.

    Args:
        path (:obj:`str`):
            The path of the document to extract the text from.

    Returns:
        :obj:`Union[ExtractedDoc, ErrorModel]`: The extracted contents
        from the document or an error if the extraction failed.
    """
    start_time = time.perf_counter()

    # Fetch file from S3.
    try:
        path = urllib.parse.unquote(path)
        doc = s3_connection.fetch_file(path)
    except s3_connection.ConnectionException as ex:
        return logger.generate_error(
            path=path,
            status_code=ex.status_code,
            exception=ex
        )
    except BotoCoreError as ex:
        return logger.generate_error(
            path=path,
            status_code=500,
            exception=ex
        )

    # Extract PDF contents.
    try:
        with fitz.open(stream=doc,
                       filetype="application/pdf") as doc:
            doc_hash = hashlib.sha256(doc.stream).hexdigest()
            toc = doc.get_toc()
            if not toc:
                toc = None
            pages = [
                dict({"number": number}, **page.get_text("dict"))
                for number, page in enumerate(doc, 1)
            ]
        elapsed_seconds = time.perf_counter() - start_time
        return ExtractedDoc(
            path=path,
            hash=doc_hash,
            elapsed_seconds=elapsed_seconds,
            toc=toc,
            pages=pages
        )
    except RuntimeError as ex:
        return logger.generate_error(
            path=path,
            status_code=500,
            exception=ex
        )


def lambda_handler(event: dict, context) -> dict:
    """AWS Lambda handler.

    See `https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html`__.

    The :obj:`event` dict contains a key ``path`` indicating the document path
    of the document to be extracted.

    Returns:
        :obj:`dict`: The extracted doc or the error details, if the extraction
        failed.
    """
    return extract(event["path"]).dict()
