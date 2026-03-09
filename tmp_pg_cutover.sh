#!/usr/bin/env bash
set -euo pipefail

cd /opt/sport-lottery-sweeper

if [[ ! -f .env.release ]]; then
  echo "[error] .env.release not found" >&2
  exit 1
fi

SNAP=$(ls -1t /opt/sport-lottery-sweeper/data/sqlite_snapshot_*.db 2>/dev/null | head -n 1 || true)
if [[ -z "${SNAP}" ]]; then
  echo "[error] sqlite snapshot not found under /opt/sport-lottery-sweeper/data" >&2
  exit 1
fi

echo "[info] using sqlite snapshot: $SNAP"

POSTGRES_DB=$(grep '^POSTGRES_DB=' .env.release | cut -d= -f2-)
POSTGRES_USER=$(grep '^POSTGRES_USER=' .env.release | cut -d= -f2-)
POSTGRES_PASSWORD=$(grep '^POSTGRES_PASSWORD=' .env.release | cut -d= -f2-)

if [[ -z "${POSTGRES_DB}" || -z "${POSTGRES_USER}" || -z "${POSTGRES_PASSWORD}" ]]; then
  echo "[error] missing postgres settings in .env.release" >&2
  exit 1
fi

PG_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"
ASYNC_PG_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

echo "[step] rebuild backend image (with asyncpg)"
docker compose --env-file .env.release -f docker-compose.edge.yml build backend

echo "[step] recreate target postgres db"
docker exec sls-postgres dropdb -U postgres --if-exists --force "$POSTGRES_DB" || true
docker exec sls-postgres createdb -U postgres "$POSTGRES_DB"

echo "[step] create schema in postgres via SQLAlchemy models"
docker compose --env-file .env.release -f docker-compose.edge.yml run --rm --no-deps \
  -e DATABASE_URL="$PG_URL" \
  -e ASYNC_DATABASE_URL="$ASYNC_PG_URL" \
  backend python - <<'PY'
import os
os.environ['DATABASE_URL'] = os.environ['DATABASE_URL']
os.environ['ASYNC_DATABASE_URL'] = os.environ['ASYNC_DATABASE_URL']
from backend.database import engine
from backend.models import Base
Base.metadata.create_all(bind=engine, checkfirst=True)
print('schema_create_ok')
PY

echo "[step] migrate data sqlite -> postgres"
SNAP_IN_CONTAINER="/work/data/$(basename "$SNAP")"
docker run --rm \
  --network sport-lottery-sweeper_sls-net \
  -v /opt/sport-lottery-sweeper:/work \
  -w /work \
  sport-lottery-sweeper-backend \
  python scripts/maintenance/migrate_sqlite_to_postgres.py \
    --sqlite-path "$SNAP_IN_CONTAINER" \
    --postgres-url "$PG_URL" \
    --batch-size 500

echo "[step] switch backend env to postgres"
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$PG_URL|" .env.release
sed -i "s|^ASYNC_DATABASE_URL=.*|ASYNC_DATABASE_URL=$ASYNC_PG_URL|" .env.release

echo "[step] rolling restart backend only"
docker compose --env-file .env.release -f docker-compose.edge.yml up -d backend

echo "[step] wait backend healthy"
for i in $(seq 1 60); do
  status=$(docker inspect --format '{{.State.Health.Status}}' sls-backend 2>/dev/null || echo "unknown")
  if [[ "$status" == "healthy" ]]; then
    echo "[ok] backend healthy"
    break
  fi
  sleep 2
  if [[ "$i" -eq 60 ]]; then
    echo "[error] backend did not become healthy in time" >&2
    docker logs --tail 200 sls-backend || true
    exit 1
  fi
done

echo "[step] verify endpoint"
code=$(curl -s -o /tmp/health.json -w '%{http_code}' http://127.0.0.1/api/v1/health/live || true)
cat /tmp/health.json || true
echo
if [[ "$code" != "200" ]]; then
  echo "[error] health endpoint http code=$code" >&2
  exit 1
fi

echo "[done] postgres cutover complete"
grep -E '^(DATABASE_URL|ASYNC_DATABASE_URL)=' .env.release
