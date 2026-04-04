#!/bin/sh
set -e

if [ -n "$POSTGRES_HOST" ]; then
  echo "Aguardando Postgres em $POSTGRES_HOST:$POSTGRES_PORT..."
  while ! nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    sleep 1
  done
fi

if [ "$(printf '%s' "${DJANGO_DEBUG:-False}" | tr '[:upper:]' '[:lower:]')" != "true" ]; then
  python manage.py check --deploy --fail-level WARNING
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
