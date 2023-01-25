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

"""Base models for the JSON schemas in all endpoints."""

import casefy
from pydantic import BaseModel


class CamelModel(BaseModel):
    """Model to handle snake_case to camelCase conversion in field names.

    Models defined for the JSON schemas of the different endpoints must inherit
    from this model, since KNOWRON uses camelCase for fields across REST APIs.
    """

    class Config:
        alias_generator = casefy.camelcase
        allow_population_by_field_name = True
