#!/bin/bash

set -e

echo "Waiting for database to be ready..."
until docker-compose exec db pg_isready -U farmtasks_user -d farmtasks_data; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $@ 