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

"""KNOWRON FOSS API.

For the API docs see "/api/v1/docs" or "/api/v1/redoc".
"""
import os
import logging
from pathlib import Path

import fitz
from dotenv import dotenv_values
from starlette.applications import Starlette
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger

from src.api import api_router_root, api_router_v1
from src.config import Environment, ENV
from src.middlewares.exception_handling import exception_handlers


gunicorn_logger = logging.getLogger("gunicorn.error")
logger.handlers = gunicorn_logger.handlers

logger.setLevel(gunicorn_logger.level)

# Shrink store size by 100 %
fitz.TOOLS.store_shrink(100)

# Instanciate app and API versions
application = Starlette()
api_root = FastAPI(
    title="KNOWRON FOSS API",
    exception_handlers=exception_handlers
)
api_v1 = FastAPI(
    title="KNOWRON FOSS API",
    version="1.0",
    # disable docs in production mode
    openapi_url="/openapi.json" if ENV is not Environment.PROD else "",
    exception_handlers=exception_handlers
)

# CORS. Specified in the .env, separated with commas, e.g.:
# CORS=https://www.one.com,https://www.two.com
# origins = dotenv_values(Path("src/.env"))["CORS"].split(",")
origins = os.environ["CORS"].split(",")
# Include middleware
application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
api_root.include_router(api_router_root)
api_v1.include_router(api_router_v1)

# Mount API routes
# Order matters! More specific routes must come first.
application.mount("/api/v1", app=api_v1)
application.mount("/", app=api_root)
