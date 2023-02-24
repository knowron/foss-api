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

"""Server initialization."""

import logging
import subprocess
from src.config import settings


def main():
    """Start up the server."""
    command = [
        "uvicorn",
        "application:app",
        "--use-colors",
        f"--log-level={logging.getLevelName(settings.get_log_level()).lower()}",
        "--port=8002"
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()

