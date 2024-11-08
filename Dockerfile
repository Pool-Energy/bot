FROM debian:bookworm-slim

LABEL maintainer="contact@pool.energy"

ARG GITHUB_TOKEN

RUN apt-get update && \
    apt-get upgrade -y
RUN apt-get install -y python3-venv python3-yaml python3-aiohttp python3-dev gcc git vim procps net-tools iputils-ping

EXPOSE 8088

RUN mkdir -p /root/bot

WORKDIR /root/bot

COPY ./requirements.txt .

RUN python3 -m venv venv
RUN ./venv/bin/pip install -r requirements.txt

COPY ./chiabot /root/bot/chiabot/
COPY ./docker/entrypoint.sh /

CMD ["bash", "/entrypoint.sh"]
