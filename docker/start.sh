#!/bin/bash

set -e

export CONFIG_FILE=${CONFIG_FILE:-/data/bot/config.yaml}

trap "killall python" TERM

cd /root/bot

exec ./venv/bin/python -m chiabot.main \
	-p pool_stats \
	-c ${CONFIG_FILE}
