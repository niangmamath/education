"""Where vetted packages are kept.

The bucket is private, per ADR-008: nothing here is ever served directly, and
the runtime origin of ADR-012 is what will hand a package to a browser. This
module only puts files in and takes them out again.

The interface is a small protocol rather than boto3 itself, so that a test can
prove what registration does with storage without needing a bucket.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import IO, Any, Protocol

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class ObjectStore(Protocol):
    """What the catalogue, and the content runtime, need from storage.

    `put`/`remove`/`get`/`presign` served the catalogue alone until the content
    runtime stopped writing to a disk shared with the origin that serves it —
    two services on a platform like Render cannot share a volume, so a deployed
    content now lives in a bucket both can reach instead. `put_bytes`,
    `remove_prefix`, `exists` and `list_prefixes` are what that move needed and
    the catalogue never did.
    """

    def put(self, key: str, path: Path) -> None: ...

    def put_bytes(self, key: str, data: bytes) -> None: ...

    def remove(self, key: str) -> None: ...

    def remove_prefix(self, prefix: str) -> None: ...

    def exists(self, key: str) -> bool: ...

    def list_prefixes(self, prefix: str) -> list[str]: ...

    def presign(self, key: str, expires_in: int, *, internal: bool = False) -> str: ...

    def get(self, key: str, path: Path) -> None: ...

    def get_object(self, key: str) -> tuple[str, IO[bytes]]: ...


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
                ContentType=_guess_content_type(key),
            )

    def put_bytes(self, key: str, data: bytes) -> None:
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=_guess_content_type(key),
        )

    def remove(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def remove_prefix(self, prefix: str) -> None:
        """Empty a prefix before laying it out again, the way `shutil.rmtree`
        emptied a directory when the runtime was still one."""
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
            if objects:
                self._client.delete_objects(
                    Bucket=self.bucket, Delete={"Objects": objects}
                )

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey"):
                return False
            raise
        return True

    def list_prefixes(self, prefix: str) -> list[str]:
        """The immediate sub-prefixes of `prefix`, the way a directory listing
        would name the folders directly under it without descending into them."""
        paginator = self._client.get_paginator("list_objects_v2")
        prefixes: list[str] = []
        for page in paginator.paginate(
            Bucket=self.bucket, Prefix=prefix, Delimiter="/"
        ):
            prefixes.extend(entry["Prefix"] for entry in page.get("CommonPrefixes", []))
        return prefixes

    def get(self, key: str, path: Path) -> None:
        """Fetch the object back, to lay it out for the runtime.

        The archive kept in the bucket is the only source of truth: deploying
        reads it back rather than trusting a copy that happens to be on disk.
        """
        with path.open("wb") as handle:
            self._client.download_fileobj(self.bucket, key, handle)

    def get_object(self, key: str) -> tuple[str, IO[bytes]]:
        """The object's content type and a readable stream of its bytes.

        Reached from `app/api/v1/internal.py`: the content origin's nginx asks
        the API for a content's bytes rather than the bucket directly, because
        the bucket's private address is one nginx can never resolve — see that
        module's own docstring for why not.
        """
        try:
            response = self._client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey"):
                raise FileNotFoundError(key) from error
            raise
        content_type = response.get("ContentType") or "application/octet-stream"
        body: IO[bytes] = response["Body"]
        return content_type, body

    def presign(self, key: str, expires_in: int, *, internal: bool = False) -> str:
        """A link that opens this object, for a short while and for no other.

        The bucket stays private, per ADR-008: nothing is ever readable without
        a signature, and a signature that outlived the session it was handed to
        would be a permanent link with extra steps.

        The public endpoint is what goes into the signature by default, because
        the address the API reaches the storage on is usually not the address a
        browser can. `internal=True` is for the one consumer that is neither:
        the content origin's nginx (`app/api/v1/internal.py`), which fetches the
        signed URL itself from inside the same private network the API is on —
        signing it against the public endpoint would hand nginx an address only
        a browser could resolve.
        """
        client = self._client if internal else self._public_client()
        url: str = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url

    def _public_client(self) -> Any:
        return boto3.client(
            "s3",
            endpoint_url=settings.S3_PUBLIC_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )


def _guess_content_type(key: str) -> str:
    """The MIME type an object should be stored under, guessed from its key.

    A browser enforces strict MIME checking on anything loaded as a `<script>`
    or a `<link rel="stylesheet">`: a `.js` served as `application/zip` is
    refused outright rather than merely mistrusted. `put`/`put_bytes` used to
    stamp everything `application/zip` unconditionally — right for the one
    thing this store first held, a `.h5p` archive nothing ever serves straight
    to a browser, and silently wrong for every library file the content runtime
    now uploads through the same two methods.
    """
    return mimetypes.guess_type(key)[0] or "application/octet-stream"
