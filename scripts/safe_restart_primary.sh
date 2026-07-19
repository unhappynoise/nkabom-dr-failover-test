#!/bin/bash

MONITOR_HOST="primarysite@192.168.57.30"
FLAG_FILE="/home/primarysite/failover/DR_IS_PRIMARY.flag"

echo "Checking failover status on monitor before restarting PostgreSQL..."

if ssh "$MONITOR_HOST" "test -f $FLAG_FILE"; then
    echo ""
    echo "!! BLOCKED !!"
    echo "A failover to DR has occurred and was never reversed."
    echo "Restarting this database now would create a SPLIT-BRAIN scenario:"
    echo "both primarysite and drsite would independently accept writes"
    echo "and their data would diverge."
    echo ""
    echo "To safely bring primarysite back:"
    echo "  1. Re-clone this database as a fresh STANDBY from drsite (now the real primary), OR"
    echo "  2. Formally fail back: promote this site again and reset drsite as the standby."
    echo ""
    echo "Once resolved, manually delete the flag on monitor:"
    echo "  ssh $MONITOR_HOST 'rm $FLAG_FILE'"
    echo ""
    exit 1
else
    echo "No unresolved failover detected. Safe to start PostgreSQL normally."
    sudo systemctl start postgresql@18-main
    exit 0
fi
