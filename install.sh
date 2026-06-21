#!/usr/bin/env bash
set -euo pipefail

# EntelekX headless installer for macOS and Linux

REPO="andreagroferreira/entelekx"
INSTALL_DIR="${ENTELEKX_INSTALL_DIR:-$HOME/.entelekx/app}"
DATA_DIR="$HOME/.entelekx"

echo "Installing EntelekX..."

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [[ "$OS" != "darwin" && "$OS" != "linux" ]]; then
  echo "Unsupported OS: $OS"
  exit 1
fi

# Ensure Python 3.12+
if ! command -v python3 &>/dev/null; then
  echo "python3 not found. Please install Python 3.12 or later."
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$(printf '%s\n' "3.12" "$PY_VERSION" | sort -V | head -n1)" != "3.12" ]]; then
  echo "Python 3.12+ required, found $PY_VERSION"
  exit 1
fi

# Ensure Node.js 22+
if ! command -v node &>/dev/null; then
  echo "Node.js not found. Please install Node.js 22 or later."
  exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//')
if [[ "$(printf '%s\n' "22.0.0" "$NODE_VERSION" | sort -V | head -n1)" != "22.0.0" ]]; then
  echo "Node.js 22+ required, found $NODE_VERSION"
  exit 1
fi

# Ensure uv
if ! command -v uv &>/dev/null; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# Ensure pnpm
if ! command -v pnpm &>/dev/null; then
  echo "Installing pnpm..."
  curl -fsSL https://get.pnpm.io/install.sh | sh -
  export PATH="$HOME/.local/share/pnpm:$PATH"
fi

# Create directories
mkdir -p "$DATA_DIR"/{data,artefacts,backups,logs}

# Download latest release or clone
if [[ "${ENTELEKX_DEV:-false}" == "true" ]]; then
  if [[ ! -d "$INSTALL_DIR" ]]; then
    echo "Cloning EntelekX repository..."
    git clone "https://github.com/$REPO.git" "$INSTALL_DIR"
  fi
  cd "$INSTALL_DIR"
  git pull origin main
else
  echo "Downloading latest EntelekX release..."
  mkdir -p "$INSTALL_DIR"
  curl -fsSL "https://github.com/$REPO/releases/latest/download/entelekx-source.tar.gz" | tar -xz -C "$INSTALL_DIR" || {
    echo "Release download failed. Falling back to git clone..."
    git clone "https://github.com/$REPO.git" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
  }
fi

# Install frontend dependencies
cd "$INSTALL_DIR"
pnpm install

# Install Python dependencies
cd "$INSTALL_DIR/packages/backend"
uv sync --extra dev

# Database setup
if ! grep -q "DATABASE_URL" "$DATA_DIR/.env" 2>/dev/null; then
  echo "Configuring database..."
  # Try Postgres.app / Homebrew detection (macOS)
  if [[ "$OS" == "darwin" ]]; then
    if command -v pg_ctl &>/dev/null; then
      echo "DATABASE_URL=postgresql://postgres@localhost/entelekx" >> "$DATA_DIR/.env"
    else
      echo "DATABASE_URL=sqlite+aiosqlite:///$DATA_DIR/data/app.db" >> "$DATA_DIR/.env"
    fi
  else
    echo "DATABASE_URL=sqlite+aiosqlite:///$DATA_DIR/data/app.db" >> "$DATA_DIR/.env"
  fi
fi

# Create .env symlink
ln -sf "$DATA_DIR/.env" "$INSTALL_DIR/.env"

# Run migrations
uv run alembic upgrade head || true

# Create systemd / launchd service (optional)
echo ""
echo "EntelekX installed to $INSTALL_DIR"
echo "Data directory: $DATA_DIR"
echo ""
echo "To start the backend:"
echo "  cd $INSTALL_DIR/packages/backend && uv run entelekx serve"
echo ""
echo "To start the desktop app:"
echo "  cd $INSTALL_DIR && pnpm dev"
