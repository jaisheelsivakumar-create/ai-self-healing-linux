#!/bin/bash
# Usage: restore.sh <archive.tar.gz> [target-dir]
set -euo pipefail

ARCHIVE="${1:?Usage: restore.sh <archive.tar.gz> [target-dir]}"
TARGET="${2:-/srv/data}"

# Verify checksum before touching filesystem
sha256sum -c "$ARCHIVE.sha256"

mkdir -p "$TARGET"
tar -xzf "$ARCHIVE" -C "$TARGET"
echo "$(date '+%F %T') Restored $ARCHIVE to $TARGET" | tee -a /srv/logs/backup.log
