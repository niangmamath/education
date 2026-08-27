# Self-hosted object storage for a platform that assigns each service its own
# port (`$PORT`) rather than letting it pick one. The published `minio/minio`
# image does not read that variable — see `start.sh` for why this replaces
# its entrypoint rather than only its command.
FROM minio/minio:latest
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT ["/start.sh"]
