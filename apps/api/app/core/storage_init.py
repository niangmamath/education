"""Ensure the buckets this platform needs exist, idempotently.

Local development creates them once with
`infrastructure/scripts/create_minio_buckets.sh`, run by a dedicated
`storage-init` step before anything else starts (`docker-compose.yml`). A
platform whose blueprint has no equivalent init step — Render's among them —
needs the same guarantee from somewhere else: the one service that always
runs before anything reads or writes a bucket, at boot, before it starts
serving. This module is that guarantee, meant to run there.

Creating a bucket that already exists is not a failure here: both MinIO and
real S3 reject it with a named error, and that specific error is read as
"already done" rather than raised.
"""

from __future__ import annotations

import sys

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

BUCKETS = (
    settings.S3_BUCKET_H5P_PACKAGES,
    settings.S3_BUCKET_H5P_RUNTIME,
    settings.S3_BUCKET_MEDIA,
    settings.S3_BUCKET_PRIVATE_EVIDENCE,
    settings.S3_BUCKET_THUMBNAILS,
)

# What both MinIO and real S3 answer for a bucket this account already owns.
ALREADY_OWNED = {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}


def main() -> int:
    client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )
    for name in BUCKETS:
        kwargs: dict[str, object] = {"Bucket": name}
        # Real S3 rejects `us-east-1` named explicitly as a location
        # constraint — it is the one region `create_bucket` expects to be
        # asked for by omission. MinIO does not care either way.
        if settings.S3_REGION != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {
                "LocationConstraint": settings.S3_REGION
            }
        try:
            client.create_bucket(**kwargs)
            print(f"{name} : créé")
        except ClientError as error:
            code = error.response.get("Error", {}).get("Code")
            if code not in ALREADY_OWNED:
                raise
            print(f"{name} : déjà présent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
