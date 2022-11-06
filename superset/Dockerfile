ARG SUPERSET_VER=2.0.0
######################################################################
# Base image...
######################################################################
FROM apache/superset:${SUPERSET_VER} AS base

RUN cd /app \
    && pip install 'pystan<3.0' \
    && pip install 'prophet>=1.0.1,<1.1' \
    && pip install psycopg2

# Switching back to using the `superset` user
USER superset

######################################################################
# Worker image with Firefox and GeckoDriver...
######################################################################
FROM base AS worker

ARG GECKODRIVER_VERSION=v0.28.0
ARG FIREFOX_VERSION=88.0

# Switching to root to install the required packages
USER root

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libnss3 libdbus-glib-1-2 libgtk-3-0 libx11-xcb1 wget

# Install GeckoDriver WebDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz -O /tmp/geckodriver.tar.gz && \
    tar xvfz /tmp/geckodriver.tar.gz -C /tmp && \
    mv /tmp/geckodriver /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Install Firefox
RUN wget https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.bz2 -O /opt/firefox.tar.bz2 && \
    tar xvf /opt/firefox.tar.bz2 -C /opt && \
    ln -s /opt/firefox/firefox /usr/local/bin/firefox

# Switching back to using the `superset` user
USER superset
