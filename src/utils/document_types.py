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
        text_block_count: int,
        image_block_count: int
    ):
        """Determine the type of a document.

        Args:
            text_block_count (:obj:`int`):
                The number of text blocks in the document.
            image_block_count (:obj:`int`):
                The number of image blocks in the document.

        Returns:
            :obj:`DocType`: The type of the document.
        """
        total_block_count = text_block_count + image_block_count
        if total_block_count == 0:
            return cls.EMPTY
        text_block_ratio = text_block_count / total_block_count
        image_block_ratio = image_block_count / total_block_count
        if text_block_ratio > image_block_ratio:
            return cls.TEXT_BASED
        return cls.IMAGE_BASED
