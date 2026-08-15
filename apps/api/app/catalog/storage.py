"""Where vetted packages are kept.

The bucket is private, per ADR-008: nothing here is ever served directly, and
the runtime origin of ADR-012 is what will hand a package to a browser. This
module only puts files in and takes them out again.

The interface is a small protocol rather than boto3 itself, so that a test can
prove what registration does with storage without needing a bucket.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import boto3

from app.core.config import settings


class ObjectStore(Protocol):
    """What registration needs from storage, and nothing more."""

    def put(self, key: str, path: Path) -> None: ...

    def remove(self, key: str) -> None: ...


class S3ObjectStore:
    """The real bucket, reached with the credentials of the configuration."""

    def __init__(self, bucket: str | None = None) -> None:
        self.bucket = bucket or settings.S3_BUCKET_H5P_PACKAGES
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )

    def put(self, key: str, path: Path) -> None:
        with path.open("rb") as handle:
            self._client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=handle,
                ContentType="application/zip",
            )

    def remove(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)
