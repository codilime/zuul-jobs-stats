#!/bin/bash
set -eu

APPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source ${APPDIR}/cron-config.sh

find ${LOGS_DIR} -name 'job-output.json.gz' -mtime 1 | xargs -n1 ${APPDIR}/main.py --setttings ${APPDIR}/settings.ini
