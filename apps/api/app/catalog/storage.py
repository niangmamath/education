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
    """What the catalogue needs from storage, and nothing more."""

    def put(self, key: str, path: Path) -> None: ...

    def remove(self, key: str) -> None: ...

    def presign(self, key: str, expires_in: int) -> str: ...

    def get(self, key: str, path: Path) -> None: ...


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

    def get(self, key: str, path: Path) -> None:
        """Fetch the object back, to lay it out for the runtime.

        The archive kept in the bucket is the only source of truth: deploying
        reads it back rather than trusting a copy that happens to be on disk.
        """
        with path.open("wb") as handle:
            self._client.download_fileobj(self.bucket, key, handle)

    def presign(self, key: str, expires_in: int) -> str:
        """A link that opens this object, for a short while and for no other.

        The bucket stays private, per ADR-008: nothing is ever readable without
        a signature, and a signature that outlived the session it was handed to
        would be a permanent link with extra steps.

        The public endpoint is what goes into the signature, because the address
        the API reaches the storage on is not the address a browser can.
        """
        client = boto3.client(
            "s3",
            endpoint_url=settings.S3_PUBLIC_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        url: str = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url
