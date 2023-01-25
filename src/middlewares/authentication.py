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

"""Authorization middlewares."""

from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette import status

from src.config import settings

API_KEY_NAME = "Authorization"
API_KEY = settings.FOSS_API_KEY
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def check_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
