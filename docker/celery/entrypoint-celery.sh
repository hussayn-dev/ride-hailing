#!/bin/sh

celery -A core worker --loglevel=info --concurrency=2 --hostname=worker1@%h --detach


exec "$@"
