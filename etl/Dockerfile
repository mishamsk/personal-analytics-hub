ARG PY_VER=3.10
FROM python:${PY_VER}

RUN mkdir /app \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    postgresql-client \
    cron \
    iputils-ping \
    nullmailer mailutils \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app \
    PATH="${PATH}:/root/.local/bin/"

COPY pyproject.toml /app/
COPY alembic /app/alembic/
COPY alembic.ini /app/
COPY dbt /app/dbt/
COPY loader /app/loader/
COPY scripts /app/scripts/

RUN python -m pip install pipx \
    && pipx install poetry==1.2.2 \
    && cd /app \
    && poetry install

WORKDIR /app

ARG PAH_SUPERSET_ADMIN_EMAIL=pah@localhost
ARG PAH_NULLMAILER_REMOTE_SPEC=""

# Set up mail
RUN echo "gmail.com" > /etc/nullmailer/defaultdomain
RUN echo "${PAH_SUPERSET_ADMIN_EMAIL}" > /etc/nullmailer/adminaddr
RUN echo "${PAH_NULLMAILER_REMOTE_SPEC}" > /etc/nullmailer/remotes
RUN chmod 666 /etc/nullmailer/remotes

ARG PAH_ETL_SCHEDULE="0 0 * * *"

# Set up cron
RUN mkdir /app/log
RUN echo "${PAH_ETL_SCHEDULE} /app/scripts/load-data.sh > /app/log/loader.log 2>&1 || sendmail -s 'Pah loader job failed' ${PAH_SUPERSET_ADMIN_EMAIL} < /app/log/loader.log" > /etc/cron.d/pah
RUN chmod 0644 /etc/cron.d/pah
RUN crontab /etc/cron.d/pah

CMD service nullmailer start && /bin/bash
