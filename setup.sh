#!/usr/bin/env bash
# ============================================================
# OpenEHRDemo — Bootstrap Script
# Installeert Docker (Debian Trixie) en start de volledige stack
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Kleuren ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ────────────────────────────────────────────────────────────
# Stap 1: Docker installeren (indien nodig)
# ────────────────────────────────────────────────────────────
install_docker() {
    info "Docker wordt geïnstalleerd vanuit de Debian repository..."
    warn "LET OP: Dit gebruikt de DEBIAN repo, NIET Ubuntu!"

    # Verwijder eventuele foute Ubuntu repo
    sudo rm -f /etc/apt/sources.list.d/docker.list
    sudo rm -f /etc/apt/keyrings/docker.gpg

    # Debian GPG key ophalen
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | \
        sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Debian repo toevoegen
    echo "deb [arch=$(dpkg --print-architecture) \
        signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Installeren
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Gebruiker toevoegen aan docker groep
    if ! groups "$USER" | grep -q docker; then
        sudo usermod -aG docker "$USER"
        warn "Je bent toegevoegd aan de docker groep."
        warn "Sluit je terminal en open opnieuw, of draai: newgrp docker"
    fi

    info "Docker is geïnstalleerd!"
    docker --version
    docker compose version
}

if ! command -v docker &> /dev/null; then
    warn "Docker is niet geïnstalleerd."
    read -p "Wil je Docker nu installeren? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        install_docker
    else
        error "Docker is vereist. Installeer het handmatig en draai dit script opnieuw."
        exit 1
    fi
else
    info "Docker is al geïnstalleerd: $(docker --version)"
fi

# Controleer of docker compose beschikbaar is
if ! docker compose version &> /dev/null; then
    error "Docker Compose plugin is niet beschikbaar. Installeer docker-compose-plugin."
    exit 1
fi

# ────────────────────────────────────────────────────────────
# Stap 2: Docker Compose starten
# ────────────────────────────────────────────────────────────
info "Docker containers starten..."
docker compose up -d

# ────────────────────────────────────────────────────────────
# Stap 3: Wachten tot EHRbase klaar is
# ────────────────────────────────────────────────────────────
EHRBASE_URL="http://localhost:8080/ehrbase/rest/status"
EHRBASE_USER="ehrbase-user"
EHRBASE_PASS="SuperSecretPassword"
MAX_WAIT=120
ELAPSED=0

info "Wachten tot EHRbase klaar is (max ${MAX_WAIT}s)..."
while ! curl -sf -u "$EHRBASE_USER:$EHRBASE_PASS" "$EHRBASE_URL" > /dev/null 2>&1; do
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        error "EHRbase is niet gestart binnen ${MAX_WAIT} seconden."
        error "Controleer: docker compose logs ehrbase"
        exit 1
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo -n "."
done
echo ""

info "EHRbase is klaar! ✅"
curl -sf -u "$EHRBASE_USER:$EHRBASE_PASS" "$EHRBASE_URL" | head -5
echo ""

# ────────────────────────────────────────────────────────────
# Stap 4: Templates uploaden
# ────────────────────────────────────────────────────────────
info "Sensire templates (v5) uploaden naar EHRbase..."
bash scripts/upload-template.sh

# ────────────────────────────────────────────────────────────
# Stap 5: Test-EHR aanmaken
# ────────────────────────────────────────────────────────────
info "Test-EHR aanmaken voor fictieve cliënt..."
bash scripts/create-ehr.sh

# ────────────────────────────────────────────────────────────
# Stap 6: Frontend dependencies installeren
# ────────────────────────────────────────────────────────────
if command -v npm &> /dev/null; then
    info "Frontend dependencies installeren..."
    cd frontend/sensire-app
    npm install
    cd "$SCRIPT_DIR"
else
    warn "npm is niet geïnstalleerd. Installeer Node.js om de frontend te draaien."
    warn "  sudo apt-get install -y nodejs npm"
fi

# ────────────────────────────────────────────────────────────
# Klaar!
# ────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          OpenEHRDemo — Setup Voltooid! ✅               ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                        ║"
echo "║  EHRbase:    http://localhost:8080                      ║"
echo "║  Swagger UI: http://localhost:8080/ehrbase/swagger-ui/  ║"
echo "║                                                        ║"
echo "║  Demo starten:                                         ║"
echo "║    cd frontend/sensire-app && npm run dev               ║"
echo "║    → Open http://localhost:5173                         ║"
echo "║                                                        ║"
echo "║  Extra tools (optioneel):                               ║"
echo "║    docker compose --profile tools up -d                 ║"
echo "║    → pgAdmin:     http://localhost:5050                 ║"
echo "║                                                        ║"
echo "║  Credentials:                                          ║"
echo "║    EHRbase:  ehrbase-user / SuperSecretPassword         ║"
echo "║    pgAdmin:  demo@sensire.nl / demo                    ║"
echo "║    Postgres: postgres / postgres                        ║"
echo "║                                                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
