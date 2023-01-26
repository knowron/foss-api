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

"""Utilities for handling the connection with AWS S3 services."""

import io
import requests

import boto3
import botocore
from fastapi import HTTPException

from src.config import settings


class S3ClientSingleton:
    """Singleton for S3 Clients.

    This singleton avoids instanciating multiple S3 clients, which is slow.
    """
    _instance = None

    def __new__(cls) -> botocore.client.BaseClient:
        """Singleton."""
        if cls._instance is None:
            cls._instance =  boto3.client(
                "s3",
                config=botocore.client.Config(signature_version="s3v4"),
                region_name=settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        return cls._instance


def fetch_file(path: str, create_new_session: bool = True) -> io.BytesIO:
    """Download a file from AWS S3.

    Args:
        path (:obj:`str`):
            The path of file on S3.
        create_new_session(:obj:`str`, `optional`, defaults to :obj:`True`):
            Whether to create a new session (and client) or not. Set to
            :obj:`True` if multithreading is used. See
            `https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html#multithreading-or-multiprocessing-with-resources`__
            If set to :obj:`False` the same (default) session and client is
            used in every call.

    Returns:
        :obj:`io.BytesIO`: The file as a `io.BytesIO` object. This object does
        not need to be closed, since it's stored in memory. See the discussion
        at `https://groups.google.com/g/django-developers/c/_ZcdWE9c2z8`__ for
        more info.

    Raises:
        :obj:`fastapi.HTTPException`: If there was any problem when fetching the
        file (e.g., it was not found).
    """
    if create_new_session:
        session = boto3.session.Session()
        s3_client = session.client(
            "s3",
            config=botocore.client.Config(signature_version="s3v4"),
            region_name=settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    else:
        s3_client = S3ClientSingleton()
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.S3_BUCKET_NAME_STRING,
            'Key': path
        }
    )
    res = requests.get(url)
    if res.status_code != 200:  # E.g., doc not found.
        raise HTTPException(
            status_code=res.status_code,
            detail=str(res.reason)
        )

    return io.BytesIO(res.content)
