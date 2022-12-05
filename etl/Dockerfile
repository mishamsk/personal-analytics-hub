ARG PY_VER=3.10
######################################################################
# Base image...
######################################################################
FROM python:${PY_VER} as base

RUN mkdir /app \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app \
    PATH="${PATH}:/root/.local/bin/"

COPY pyproject.toml /app/
COPY scripts /app/scripts/
COPY loader /app/loader/

RUN python -m pip install pipx \
    && pipx install poetry==1.2.2 \
    && cd /app \
    && poetry install

WORKDIR /app
######################################################################
# Full image with mailer & cron...
######################################################################
FROM base as full

ARG PAH_SUPERSET_ADMIN_EMAIL=pah@localhost
ARG PAH_NULLMAILER_REMOTE_SPEC=""

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cron \
    iputils-ping \
    nullmailer mailutils \
    && rm -rf /var/lib/apt/lists/* \
    && which cron \
    && rm -rf /etc/cron.*/*

# Set up mail
RUN echo "gmail.com" > /etc/nullmailer/defaultdomain
RUN echo "${PAH_SUPERSET_ADMIN_EMAIL}" > /etc/nullmailer/adminaddr
RUN echo "${PAH_NULLMAILER_REMOTE_SPEC}" > /etc/nullmailer/remotes
RUN chmod 666 /etc/nullmailer/remotes

ENTRYPOINT ["scripts/entrypoint.sh"]

CMD ["cron","-f", "-L", "2"]
