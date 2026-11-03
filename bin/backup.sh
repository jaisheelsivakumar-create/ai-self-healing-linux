#!/bin/bash
# Snapshot-based backup of /srv/data with checksum, config backup and retention
set -euo pipefail

VG="vg_data"
LV="lv_data"
SNAP="snap_backup"
MNT="/mnt/snap_backup"
DEST="/backup"
TS=$(date +%F_%H%M%S)
LOG="/srv/logs/backup.log"
KEEP_DAYS=7

log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

cleanup() {
    if mountpoint -q "$MNT"; then umount "$MNT"; fi
    if lvs "$VG/$SNAP" >/dev/null 2>&1; then lvremove -y "$VG/$SNAP" >/dev/null; fi
    rmdir "$MNT" 2>/dev/null || true
}

trap cleanup EXIT
trap 'log "FAILED at line $LINENO"' ERR

mkdir -p "$DEST/daily" "$DEST/config" "$MNT"
log "START backup $TS"

# 1. Consistent point-in-time snapshot
lvcreate -s -n "$SNAP" -L 1G "/dev/$VG/$LV" >/dev/null
mount -o ro,nouuid "/dev/$VG/$SNAP" "$MNT"

# 2. Archive and checksum
ARCHIVE="$DEST/daily/data-$TS.tar.gz"
tar -czf "$ARCHIVE" -C "$MNT" .
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"

# 3. System configuration and LVM metadata
tar -czf "$DEST/config/etc-$TS.tar.gz" -C / etc
vgcfgbackup -f "$DEST/config/$VG-$TS.vg" "$VG" >/dev/null

# 4. Retention: prune old archives
find "$DEST" -type f -mtime +"$KEEP_DAYS" -delete

log "SUCCESS $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"
