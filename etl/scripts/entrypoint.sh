#!/usr/bin/env bash

# Start mailer
service nullmailer start

# Copy environment variables for cron jobs
export > /etc/environment

# Set up cron
echo "SHELL=/bin/bash" > /etc/crontab
echo "BASH_ENV=/etc/environment" >> /etc/crontab
echo "MAILTO=\"${PAH_SUPERSET_ADMIN_EMAIL}\"" >> /etc/crontab
echo "${PAH_ETL_SCHEDULE:-0 0 * * *} root /app/scripts/load-data.sh >/proc/1/fd/1" >> /etc/crontab
echo "# Empty line to make cron happy" >> /etc/crontab

cat /etc/crontab

# execute CMD
echo "$@"
exec "$@"
