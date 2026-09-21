#!/bin/bash
# SPDX-License-Identifier: MIT
# Install stream-page.service on the always-on workstation. Mirrors the benches' installers:
# fills in the repo path and user from the current checkout.
#   systemd/install.sh            # install and enable
#   systemd/install.sh --now      # and start it
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RUN_USER="${SUDO_USER:-$USER}"

command -v caddy >/dev/null || { echo "caddy not installed (apt: caddy-stable repo)" >&2; exit 1; }
if [[ ! -f /etc/default/stream-page ]]; then
    cat >&2 <<'EOF'
/etc/default/stream-page is missing. Create it (root, 0644) with:
  STREAM_BIND=<address(es) to listen on, space-separated>
  STREAM_PORT=8088
  HAILO_UPSTREAM=<hailo bench host>:8080
  ORIN_UPSTREAM=<orin bench host>:8080
Values are in the private wk-inventory repo.
EOF
    exit 1
fi

echo "Installing stream-page.service (user=$RUN_USER, repo=$REPO_DIR)"
sed -e "s|__USER__|$RUN_USER|g" -e "s|__REPO_DIR__|$REPO_DIR|g" \
    "$SCRIPT_DIR/stream-page.service" | sudo tee /etc/systemd/system/stream-page.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable ${1:-} stream-page.service

echo ""
echo "  sudo systemctl start|stop|restart stream-page"
echo "  journalctl -u stream-page -f"
