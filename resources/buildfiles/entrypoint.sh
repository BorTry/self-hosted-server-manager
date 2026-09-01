#!/bin/sh
set -euo pipefail

if [ -f /data/.initialized ]; then
    i=0

    while :; do
        var="LAUNCH_ARG_$i"

        # Check whether the variable exists
        eval "is_set=\${$var+x}"

        [ "$is_set" = "x" ] || break

        # Retrieve its value
        eval "value=\${$var}"

        # Debug output
        echo "$var = [$value]"

        # Append it as exactly one argument
        set -- "$@" "$value"

        i=$((i + 1))
    done

    echo "Launching /app/server with $# argument(s):"

    i=1
    for arg in "$@"; do
        echo "  arg $i = [$arg]"
        i=$((i + 1))
    done

    exec gosu server_user "$@"
else
    if [ -n "${SEED_SCRIPT:-}" ]; then
        gosu server_user sh -c 'set -e; eval "$1"' sh "$SEED_SCRIPT"
    fi

    touch /data/.initialized
fi