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

from enum import Enum

from config import settings


class DocType(Enum):
    """The type of document.

    Attributes:
        EMPTY:
            An empty document.
        TEXT_BASED:
            A text-based document.
        IMAGE_BASED:
            An image-based document.
    """

    EMPTY = "empty"
    TEXT_BASED = "text_based"
    IMAGE_BASED = "image_based"

    @classmethod
    def determine(
        cls,
        text_count: int,
        image_count: int,
        drawing_count: int
    ):
        """Determine the type of a document.

        Args:
            text_count (:obj:`int`):
                The number of text blocks in the document.
            image_count (:obj:`int`):
                The number of images in the document.
            drawing_count (:obj:`int`):
                The number of drawings in the document.

        Returns:
            :obj:`DocType`: The type of the document.
        """
        total_count: int = (
            text_count + image_count + drawing_count
        )
        if total_count == 0:
            return cls.EMPTY
        text_ratio = text_count / total_count
        image_ratio = image_count / total_count
        if text_ratio > image_ratio:
            return cls.TEXT_BASED
        # Note: If there is no text but there are drawings, we also consider
        # the doc image-based.
        return cls.IMAGE_BASED
