FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=Europe/Madrid
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata util-linux build-essential \
    && ln -snf /usr/share/zoneinfo/Europe/Madrid /etc/localtime \
    && echo Europe/Madrid > /etc/timezone \
    && useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin bot \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts/ /app/scripts/
COPY run_job.py /app/run_job.py
COPY crontab /etc/cron.d/telegram-jobs
COPY entrypoint.sh /usr/local/bin/telegram-entrypoint
RUN chmod 0644 /etc/cron.d/telegram-jobs \
    && chmod 0755 /usr/local/bin/telegram-entrypoint
ENTRYPOINT ["/usr/local/bin/telegram-entrypoint"]
