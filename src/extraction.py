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
import json
import time
import urllib.parse
from pathlib import Path
from typing import Union, Dict

import fitz
from fitz import sRGB_to_rgb
from botocore.exceptions import BotoCoreError

from config import settings
from utils import s3_connection
from utils.document_types import DocType
from utils.logging_utils import Logger, ErrorModel
from utils.models import Success


logger = Logger(name=__name__)


def extract(path: str) -> Union[Success, ErrorModel]:
    """Extract the text of a PDF.

    Args:
        path (:obj:`str`):
            The path of the document to extract the text from.

    Returns:
        :obj:`Union[Success, ErrorModel]`: The S3 key to the extracted contents
        from the document or an error if the extraction failed.
    """
    start_time = time.perf_counter()

    # Fetch file from S3.
    try:
        path = urllib.parse.unquote(path)
        doc = s3_connection.fetch_file(path, settings.DOCS_S3_BUCKET_NAME)
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
            pages = []
            block_type_counts: Dict[str, int] = {
                "text": 0,
                "image": 0
            }
            for number, raw_page in enumerate(doc, 1):
                page = dict(
                    {"number": number,
                     "rotation": raw_page.rotation},
                    **raw_page.get_text("dict")
                )
                # Images can appear referenced at the page level or included
                # as an image block (handled below).
                block_type_counts["image"] += len(raw_page.get_images())
                for block in page["blocks"]:
                    if block["type"] == 0:  # text
                        block_type_counts["text"] += 1
                        for line in block["lines"]:
                            for span in line["spans"]:
                                # Encode the text in UTF-8. If the text cannot
                                # be encoded, it is ignored.
                                try:
                                    span["text"].encode("utf-8")
                                except ValueError:
                                    span["text"] = ""
                                # Transform the color from sRGB to hexadecimal
                                # (preceded by '#').
                                if not isinstance(span["color"], str):
                                    r, g, b = sRGB_to_rgb(span["color"])
                                    span["color"] = f"#{r:02x}{g:02x}{b:02x}"
                    elif block["type"] == 1:  # image
                        block_type_counts["image"] += 1
                        # For now, we don't return images to reduce the response
                        # size.
                        block["image"] = ""
                # `dict.fromkeys` is used to remove duplicates keeping the order.
                page["line_drawings"] = list(dict.fromkeys(
                    (round(item[1][0], 2),  # x0
                     round(item[1][1], 2),  # y0
                     round(item[2][0], 2),  # x1
                     round(item[2][1], 2))  # y1
                    for drawing in raw_page.get_drawings()
                    for item in drawing["items"]
                    if item[0] == "l"
                ))
                pages.append(page)
        elapsed_seconds = time.perf_counter() - start_time
        doc_type: DocType = DocType.determine(
            block_type_counts["text"],
            block_type_counts["image"]
        )
        if doc_type in (DocType.EMPTY, DocType.IMAGE_BASED):
            key = None
        elif doc_type is DocType.TEXT_BASED:
            extracted_doc = {
                "path": path,
                "hash": doc_hash,
                "elapsed_seconds": round(elapsed_seconds, 2),
                "toc": toc,
                "pages": pages
            }
            filepath = (Path("/tmp")/f"{path}").with_suffix('.json')
            filepath.parents[0].mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(extracted_doc, f)
            key = s3_connection.upload_file(
                filepath,
                settings.EXTRACTED_S3_BUCKET_NAME
            )
            filepath.unlink(missing_ok=True)
        else:
            raise NotImplementedError(f'unrecognized doc type "{doc_type}"')
        return Success(doc_hash=doc_hash, key=key, doc_type=doc_type.value)
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
    return extract(event["path"]).model_dump()
