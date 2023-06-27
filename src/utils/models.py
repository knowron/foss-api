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

import base64
from typing import List, Optional, Tuple, Union

from pydantic import validator, constr
from fitz import sRGB_to_rgb

from config import settings
from utils.base_model import CamelModel


class Span(CamelModel):
    """A span in a line.

    For info about its attributes, see
    `https://pymupdf.readthedocs.io/en/latest/textpage.html#span-dictionary`__.
    """

    size: float
    flags: int
    font: str
    color: str
    ascender: float
    descender: float
    text: str
    origin: Tuple[float, float]
    bbox: Tuple[float, float, float, float]

    @validator("color", pre=True, always=True)
    def color_to_hex(cls, color: str) -> str:
        """Transform the color from sRGB to hexadecimal (preceded by '#')."""
        if isinstance(color, str):
            return color
        r, g, b = sRGB_to_rgb(color)
        return f"#{r:02x}{g:02x}{b:02x}"

    @validator("text", pre=True, always=True)
    def encode_text_utf8(cls, text: str) -> str:
        """Encode the text in UTF-8.

        If the text cannot be encoded, it is ignored.
        """
        try:
            return text.encode("utf-8")
        except ValueError:
            return ""


class Line(CamelModel):
    """A line block.

    For info about its attributes, see
    `https://pymupdf.readthedocs.io/en/latest/textpage.html#line-dictionary`__.
    """

    spans: List[Span]
    wmode: int
    dir: Tuple[float, float]
    bbox: Tuple[float, float, float, float]


class TextBlock(CamelModel):
    """A text block.

    For info about its attributes, see
    `https://pymupdf.readthedocs.io/en/latest/textpage.html#page-dictionary`__.
    """

    number: int
    type: int = 0
    bbox: Tuple[float, float, float, float]
    lines: List[Line]


class ImageBlock(CamelModel):
    """An image block.

    For info about its attributes, see
    `https://pymupdf.readthedocs.io/en/latest/textpage.html#page-dictionary`__.


    .. note::

       The field :attr:`image` is returned Base64-encoded.
    """

    number: int
    type: int = 1
    bbox: Tuple[float, float, float, float]
    width: int
    height: int
    ext: str
    colorspace: int 
    xres: int
    yres: int
    bpc: int
    transform: Tuple[float, float, float, float, float, float]
    size: int
    image: Union[bytes, str]

    @validator("image")
    def encode_image_base64(cls, image: bytes) -> str:
        """Encode images in Base64 to avoid serialization issues.

        .. warning::

           Images are ignored for now to reduce the response size.
        """
        return ""
        # return base64.b64encode(image)  # b64encode returns bytes


class Page(CamelModel):
    """A page in an extracted document.

    Attributes:
        number (:obj:`str`):
            The page number. The first page is ``1``, not ``0``.
        width (:obj:`float`):
            The width of the page.
        height (:obj:`float`):
            The height of the page.
        blocks (:obj:`List[Union[TextBlock, ImageBlock]]`):
            The blocks that the page contain. These can be text blocks or image
            blocks.
    """

    number: int  # 1-indexed
    width: float
    height: float
    blocks: List[Union[TextBlock, ImageBlock]]


class ExtractedDoc(CamelModel):
    """An extracted document.

    Attributes:
        path (:obj:`str`):
            The document path.
        hash (:obj:`str`):
            The SHA-256 hash of the document binary.
        elapsed_seconds (:obj:`float`):
            The number of seconds it took to process and extract the content of
            the document.
        toc (:obj:`Optional[List[List[Union[int, str]]]]`):
            The Table of Contents (Outlines) of the document. :obj:`None` if the
            document has no ToC. The format of this field follows what
            :meth:`fitz.Document.get_toc()` returns, e.g.::

               [[1, '1\tAbout these instructions', 4]], ...]

            I.e.: Each element in the list is an entry of the ToC. Each entry
            is itself a list with three elements: its level, title and target
            page.
        pages (:obj:`List[Page]`):
            The (extracted) pages of the document.
    """

    path: str
    hash: constr(min_length=64, max_length=64)
    elapsed_seconds: float
    extraction_version: str = settings.EXTRACTION_VERSION
    toc: Optional[List[List[Union[int, str]]]]
    pages: List[Page]

    @validator("elapsed_seconds", pre=True, always=True)
    def round_elapsed_seconds(cls, elapsed_seconds: float) -> float:
        """Round the elapsed time (in seconds) to 2 decimals."""
        return round(elapsed_seconds, 2)


class Success(CamelModel):
    """Response model when the extraction was successful.

    Attributes:
        success (:obj:`bool`):
            Whether the extraction succeeded. Always set to ``True``.
        key (:obj:`str`):
            The S3 key to the extracted contents.
    """
    success: bool = True
    key: str
