FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        python3-venv python3-yaml python3-aiohttp python3-dev \
        gcc git vim procps net-tools iputils-ping

EXPOSE 8088

WORKDIR /root/bot

COPY ./requirements.txt .

RUN python3 -m venv venv && \
    ./venv/bin/pip install -r requirements.txt

COPY ./chiabot /root/bot/chiabot/
COPY ./docker/entrypoint.sh /

CMD ["/bin/bash", "/entrypoint.sh"]
