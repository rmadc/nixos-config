FROM python:3.11-slim-bookworm

ARG JOB
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=Europe/Madrid JOB_NAME=${JOB}
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata util-linux build-essential \
    && ln -snf /usr/share/zoneinfo/Europe/Madrid /etc/localtime \
    && echo Europe/Madrid > /etc/timezone \
    && useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin bot \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY jobs/${JOB}/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY jobs/${JOB}/main.py /app/jobs/${JOB}/main.py
COPY jobs/${JOB}/crontab /etc/cron.d/telegram-job
COPY run_job.py /app/run_job.py
COPY entrypoint.sh /usr/local/bin/telegram-entrypoint
RUN chmod 0644 /etc/cron.d/telegram-job \
    && chmod 0755 /usr/local/bin/telegram-entrypoint
ENTRYPOINT ["/usr/local/bin/telegram-entrypoint"]
