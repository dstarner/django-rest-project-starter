#!/bin/bash
set -e

[[ "$*" == *"runserver"* ]] && ./manage.py collectstatic --no-input

# Allows for a wait period before spinning up
sleep ${PRE_RUN_SLEEP:=0}

exec "$@"