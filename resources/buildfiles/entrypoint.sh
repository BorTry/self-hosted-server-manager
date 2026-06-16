#!/bin/sh
set -e

if [ ! -f /data/.aclinitialized ]; then
    chown -R server_user:server_user /data
    chmod -R u+rwx /data

    touch /data/.aclinitialized
fi

if [ ! -f /data/.initialized ] && [ -n "$SEED_SCRIPT" ]; then
    eval "$SEED_SCRIPT"

    touch /data/.initialized
fi

exec gosu server_user "$@"