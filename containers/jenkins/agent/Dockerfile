# The standard agent plus the tools our pipeline needs.
FROM jenkins/inbound-agent:3396.ve02b_5cde31b_2-5-jdk21

# Installing packages needs root.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends shellcheck python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/ruff \
    && /opt/ruff/bin/pip install --no-cache-dir ruff \
    && ln -s /opt/ruff/bin/ruff /usr/local/bin/ruff

# Run builds as the unprivileged user again.
USER jenkins