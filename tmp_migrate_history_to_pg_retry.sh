#!/usr/bin/env bash
set -euo pipefail
cd /opt/sport-lottery-sweeper

POSTGRES_DB=$(grep '^POSTGRES_DB=' .env.release | cut -d= -f2- | tr -d '\r')
POSTGRES_USER=$(grep '^POSTGRES_USER=' .env.release | cut -d= -f2- | tr -d '\r')
POSTGRES_PASSWORD=$(grep '^POSTGRES_PASSWORD=' .env.release | cut -d= -f2- | tr -d '\r')
PG_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

printf '[run migration only]\n'
docker run --rm \
  --network sport-lottery-sweeper_sls-net \
  -v /opt/sport-lottery-sweeper:/work \
  -w /work \
  sport-lottery-sweeper-backend \
  python scripts/maintenance/migrate_sqlite_to_postgres.py \
    --sqlite-path /work/data/historical_sport_lottery_20260226.db \
    --postgres-url "$PG_URL" \
    --batch-size 500

printf '[after counts]\n'
docker exec sls-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -F '|' -c "SELECT 'matches', COUNT(1) FROM matches UNION ALL SELECT 'football_matches', COUNT(1) FROM football_matches UNION ALL SELECT 'draw_features', COUNT(1) FROM draw_features UNION ALL SELECT 'poisson_11_results', COUNT(1) FROM poisson_11_results UNION ALL SELECT 'intel_collection_items', COUNT(1) FROM intel_collection_items UNION ALL SELECT 'teams', COUNT(1) FROM teams UNION ALL SELECT 'log_entries', COUNT(1) FROM log_entries;"
