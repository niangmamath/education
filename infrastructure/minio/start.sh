#!/bin/sh
# Render assigns a `$PORT` and expects the service to listen exactly there —
# confirmed by "Port scan timeout reached, no open ports detected" the first
# time this ran the base image unmodified, `minio server /data` bound to its
# own hardcoded 9000 regardless of what Render was probing.
#
# This replaces the base image's own entrypoint rather than only its CMD: that
# entrypoint prepends `minio` to whatever argument it is given that isn't
# already `minio` (`set -- minio "$@"`), so a CMD naming this script would
# have been run as `minio /start.sh` instead of running it. Nothing else in
# the base entrypoint applies here — its remaining logic is a deprecated
# user-switch this image never sets the variables for.
set -e
exec minio server /data --address ":${PORT:-9000}"
