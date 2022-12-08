#! /bin/bash

set -e


APP_MODULE=${APP_MODULE:-src/app:app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}
RELOAD=${RELOAD:-true}
ACCESSLOG=${ACCESSLOG:-true}
ERRORLOG=${ERRORLOG:-true}

args=("hypercorn" "--bind" "$HOST:$PORT" "--log-level" "$LOG_LEVEL")

[ ! -z "$RELOAD" ] && args+=("--reload")
[ ! -z "$ACCESSLOG" ] && args+=("--access-logfile" "-")
[ ! -z "$ERRORLOG" ] && args+=("--error-logfile" "-")
[ ! -z "$WORKERS" ] && args+=("--root-path" "$WORKERS");
[ ! -z "$ROOT_PATH" ] && args+=("--root-path" "$ROOT_PATH")

args+=("$APP_MODULE")

for e in "${args[@]}"
do
    cmd=${cmd:+$cmd }$e
done

if [ ! -z "$DB_MIGRATE" ]; then
    alembic -c alembic/auth/conf.ini upgrade heads
fi

echo "Running server: $cmd"
exec $cmd
