#!/bin/sh
set -e

echo "[auth] Esperando PostgreSQL en ${DB_HOST}:${DB_PORT}..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        dbname=os.environ['DB_NAME'], user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'], host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'], connect_timeout=3
    )
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
    printf '.'
    sleep 2
done
echo " PostgreSQL listo."

echo "[auth] Creando migraciones..."
python manage.py makemigrations core --noinput 2>/dev/null || true

echo "[auth] Aplicando migraciones..."
python manage.py migrate --noinput

echo "[auth] Archivos estáticos..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

echo "[auth] Creando superusuario admin..."
python manage.py ensure_superuser

echo "[auth] Iniciando Gunicorn (workers=${GUNICORN_WORKERS:-4})..."
exec gunicorn auth_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -
