#!/bin/bash

set -e

trap "killall python" TERM

cd /root/bot

exec ./venv/bin/python -m chiabot.main \
	-p ${PLUGIN_LIST:-""} \
	-c ${CONFIG_FILE:-/data/bot/config.yaml}
