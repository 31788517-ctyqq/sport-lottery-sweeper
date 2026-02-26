#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"
PROJECT_DIR="${3:-/opt/sport-lottery-sweeper}"
ENV_FILE="$PROJECT_DIR/.env.release"

if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
  echo "Usage: $0 <domain> <email> [project_dir]"
  exit 1
fi

# Normalize domain input to apex domain.
DOMAIN="${DOMAIN#http://}"
DOMAIN="${DOMAIN#https://}"
DOMAIN="${DOMAIN%%/*}"
DOMAIN="${DOMAIN#www.}"
WWW_DOMAIN="www.${DOMAIN}"
CLI_DOMAIN="$DOMAIN"

if [[ "$(id -u)" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

random_alnum() {
  local length="${1:-32}"
  local value=""
  while [[ "${#value}" -lt "$length" ]]; do
    value+=$(openssl rand -base64 48 | tr -dc 'A-Za-z0-9')
  done
  printf '%s' "${value:0:length}"
}

random_hex() {
  local bytes="${1:-32}"
  openssl rand -hex "$bytes"
}

if ! command -v docker >/dev/null 2>&1; then
  echo "[setup] Installing Docker..."
  if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update
    $SUDO apt-get install -y ca-certificates curl gnupg
    $SUDO install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    $SUDO chmod a+r /etc/apt/keyrings/docker.gpg
    . /etc/os-release
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
      | $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null
    $SUDO apt-get update
    $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf -y install dnf-plugins-core
    $SUDO dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    $SUDO dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  elif command -v yum >/dev/null 2>&1; then
    $SUDO yum -y install yum-utils
    $SUDO yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    $SUDO yum -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  else
    echo "[error] Unsupported Linux distribution: no apt-get/dnf/yum found."
    exit 1
  fi
fi

if command -v systemctl >/dev/null 2>&1; then
  $SUDO systemctl enable --now docker >/dev/null 2>&1 || true
fi

DOCKER="docker"
if ! docker info >/dev/null 2>&1; then
  if [[ -n "$SUDO" ]] && sudo docker info >/dev/null 2>&1; then
    DOCKER="$SUDO docker"
  fi
fi

COMPOSE_IMPL=""
if $DOCKER compose version >/dev/null 2>&1; then
  COMPOSE_IMPL="docker"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_IMPL="docker-compose"
else
  echo "[error] Docker Compose is not available."
  exit 1
fi

compose_cmd() {
  if [[ "$COMPOSE_IMPL" == "docker" ]]; then
    $DOCKER compose "$@"
  else
    if [[ -n "$SUDO" ]]; then
      $SUDO docker-compose "$@"
    else
      docker-compose "$@"
    fi
  fi
}

$SUDO mkdir -p "$PROJECT_DIR"
$SUDO chown -R "$(id -un)":"$(id -gn)" "$PROJECT_DIR"
cd "$PROJECT_DIR"

mkdir -p deploy/nginx/ssl deploy/certbot/webroot deploy/certbot/etc deploy/certbot/var

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[setup] Creating release env file: $ENV_FILE"
  POSTGRES_DB="sport_lottery"
  POSTGRES_USER="postgres"
  POSTGRES_PASSWORD="$(random_alnum 32)"
  SECRET_KEY="$(random_hex 32)"
  CORS_ORIGINS="https://$DOMAIN,https://$WWW_DOMAIN"
  DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB"
  ASYNC_DATABASE_URL="postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB"
  cat > "$ENV_FILE" <<EOF
DOMAIN=$DOMAIN
CERTBOT_EMAIL=$EMAIL
ENVIRONMENT=production
DEBUG=false
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
DATABASE_URL=$DATABASE_URL
ASYNC_DATABASE_URL=$ASYNC_DATABASE_URL
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$SECRET_KEY
CORS_ORIGINS=$CORS_ORIGINS
ALLOWED_ORIGINS=$CORS_ORIGINS
EOF
  chmod 600 "$ENV_FILE"
fi

sed -i 's/\r$//' "$ENV_FILE"

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

POSTGRES_DB="${POSTGRES_DB:-sport_lottery}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(random_alnum 32)}"
SECRET_KEY="${SECRET_KEY:-$(random_hex 32)}"
REDIS_URL="${REDIS_URL:-redis://redis:6379/0}"
ENVIRONMENT="${ENVIRONMENT:-production}"
DEBUG="${DEBUG:-false}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-$EMAIL}"
CORS_ORIGINS="${CORS_ORIGINS:-https://$CLI_DOMAIN,https://www.$CLI_DOMAIN}"
DATABASE_URL="${DATABASE_URL:-postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB}"
ASYNC_DATABASE_URL="${ASYNC_DATABASE_URL:-postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB}"

# Keep CLI domain as source of truth, ignore stale DOMAIN from env file.
DOMAIN="$CLI_DOMAIN"
WWW_DOMAIN="www.${CLI_DOMAIN}"

cat > "$ENV_FILE" <<EOF
DOMAIN=$DOMAIN
CERTBOT_EMAIL=$CERTBOT_EMAIL
ENVIRONMENT=$ENVIRONMENT
DEBUG=$DEBUG
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
DATABASE_URL=$DATABASE_URL
ASYNC_DATABASE_URL=$ASYNC_DATABASE_URL
REDIS_URL=$REDIS_URL
SECRET_KEY=$SECRET_KEY
CORS_ORIGINS=$CORS_ORIGINS
ALLOWED_ORIGINS=$CORS_ORIGINS
EOF
chmod 600 "$ENV_FILE"

if [[ ! -s deploy/nginx/ssl/fullchain.pem || ! -s deploy/nginx/ssl/privkey.pem ]]; then
  echo "[setup] Generating temporary self-signed certificate..."
  openssl req -x509 -nodes -newkey rsa:2048 -days 7 \
    -keyout deploy/nginx/ssl/privkey.pem \
    -out deploy/nginx/ssl/fullchain.pem \
    -subj "/CN=${DOMAIN}" >/dev/null 2>&1
fi

sed "s/__DOMAIN__/${DOMAIN}/g" deploy/nginx/nginx.edge.template.conf > deploy/nginx/nginx.edge.conf

echo "[setup] Starting production stack..."
compose_cmd --env-file "$ENV_FILE" -f docker-compose.edge.yml up -d --build

echo "[setup] Requesting Let's Encrypt certificate..."
if $DOCKER run --rm \
  -v "$PROJECT_DIR/deploy/certbot/etc:/etc/letsencrypt" \
  -v "$PROJECT_DIR/deploy/certbot/var:/var/lib/letsencrypt" \
  -v "$PROJECT_DIR/deploy/certbot/webroot:/var/www/certbot" \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d "$DOMAIN" -d "$WWW_DOMAIN" \
  --email "$CERTBOT_EMAIL" --agree-tos --no-eff-email --non-interactive; then
  cp "deploy/certbot/etc/live/$DOMAIN/fullchain.pem" deploy/nginx/ssl/fullchain.pem
  cp "deploy/certbot/etc/live/$DOMAIN/privkey.pem" deploy/nginx/ssl/privkey.pem
  compose_cmd --env-file "$ENV_FILE" -f docker-compose.edge.yml exec -T reverse-proxy nginx -s reload
  echo "[setup] Let's Encrypt certificate applied."
else
  echo "[warn] Let's Encrypt issuance failed; still running with temporary self-signed certificate."
fi

cat > deploy/remote/renew-certs.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
DOMAIN="${1:?domain required}"
EMAIL="${2:?email required}"
PROJECT_DIR="${3:-/opt/sport-lottery-sweeper}"
ENV_FILE="$PROJECT_DIR/.env.release"
cd "$PROJECT_DIR"
DOCKER="docker"
if ! docker info >/dev/null 2>&1; then
  if sudo docker info >/dev/null 2>&1; then
    DOCKER="sudo docker"
  fi
fi
COMPOSE_IMPL=""
if $DOCKER compose version >/dev/null 2>&1; then
  COMPOSE_IMPL="docker"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_IMPL="docker-compose"
else
  echo "Docker Compose is not available."
  exit 1
fi
compose_cmd() {
  if [[ "$COMPOSE_IMPL" == "docker" ]]; then
    $DOCKER compose "$@"
  else
    if command -v sudo >/dev/null 2>&1; then
      sudo docker-compose "$@"
    else
      docker-compose "$@"
    fi
  fi
}
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
$DOCKER run --rm \
  -v "$PROJECT_DIR/deploy/certbot/etc:/etc/letsencrypt" \
  -v "$PROJECT_DIR/deploy/certbot/var:/var/lib/letsencrypt" \
  -v "$PROJECT_DIR/deploy/certbot/webroot:/var/www/certbot" \
  certbot/certbot renew --webroot -w /var/www/certbot --quiet
if [[ -f "deploy/certbot/etc/live/$DOMAIN/fullchain.pem" ]]; then
  cp "deploy/certbot/etc/live/$DOMAIN/fullchain.pem" deploy/nginx/ssl/fullchain.pem
  cp "deploy/certbot/etc/live/$DOMAIN/privkey.pem" deploy/nginx/ssl/privkey.pem
  compose_cmd --env-file "$ENV_FILE" -f docker-compose.edge.yml exec -T reverse-proxy nginx -s reload
fi
EOF

chmod +x deploy/remote/renew-certs.sh

echo "[done] Deployment finished."
echo "URL: https://$DOMAIN"
