#!/bin/bash

set -Eeuo pipefail

script_dir=$(realpath "$(dirname "${BASH_SOURCE[0]}")")

trap cleanup SIGINT SIGTERM ERR EXIT

parse_params() {
  # default values of variables set from params
  dotenv=0
  param=''

  while :; do
    case "${1-}" in
    # -h | --help) usage ;;
    -v | --verbose) set -x ;;
    -e | --dotenv) dotenv=1 ;;
    # example named parameter 
    # -p | --param) 
    #   param="${2-}"
    #   shift
    #   ;;
    -?*) die "Unknown option: $1" ;;
    *) break ;;
    esac
    shift
  done

  args=("$@")

  # check required params and arguments
  #[[ -z "${param-}" ]] && die "Missing required parameter: param"
  #[[ ${#args[@]} -eq 0 ]] && die "Missing script arguments"

}

main() {
    [[ $dotenv > 0 ]] && set -a; source .env; set +a;

    APP_MODULE=${APP_MODULE:-src/app:app}
    HOST=${HOST:-0.0.0.0}
    PORT=${PORT:-8000}
    LOG_LEVEL=${LOG_LEVEL:-info}
    RELOAD=${RELOAD:-true}
    ACCESSLOG=${ACCESSLOG:-true}
    ERRORLOG=${ERRORLOG:-true}
    WORKERS=${WORKERS:-}
    ROOT_PATH=${ROOT_PATH:-}

    chunks=("hypercorn" "--bind" "$HOST:$PORT" "--log-level" "$LOG_LEVEL")

    [[ "$RELOAD" == "true" ]] && chunks+=("--reload")
    [[ "$ACCESSLOG" == "true" ]] && chunks+=("--access-logfile" "-")
    [[ "$ERRORLOG" == "true" ]] && chunks+=("--error-logfile" "-")
    [[ ! -z "$WORKERS" ]] && chunks+=("--workers" "$WORKERS");
    [[ ! -z "$ROOT_PATH" ]] && chunks+=("--root-path" "$ROOT_PATH")

    chunks+=("$APP_MODULE")

    for e in "${chunks[@]}"
    do
        cmd=${cmd:+$cmd }$e
    done

    msg "Running server: $cmd"
    exec $cmd
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}


parse_params "$@"
main
