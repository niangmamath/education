#!/bin/sh
set -eu
mc alias set local http://storage:9000 "$S3_ACCESS_KEY" "$S3_SECRET_KEY"
for bucket in \
  "$S3_BUCKET_H5P_PACKAGES" \
  "$S3_BUCKET_H5P_RUNTIME" \
  "$S3_BUCKET_MEDIA" \
  "$S3_BUCKET_PRIVATE_EVIDENCE" \
  "$S3_BUCKET_THUMBNAILS"
do
  mc mb --ignore-existing "local/$bucket"
  mc anonymous set none "local/$bucket"
done
printf '%s\n' 'Buckets locaux prives initialises.'
