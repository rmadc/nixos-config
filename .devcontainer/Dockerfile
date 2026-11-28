# Development tools. Same Python version as the Telegram job images.
FROM python:3.11-slim-bookworm

# Keep __pycache__ folders out of the working copy.
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git shellcheck \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir ruff pytest \
    && useradd --create-home --shell /bin/bash --uid 1000 dev

USER dev