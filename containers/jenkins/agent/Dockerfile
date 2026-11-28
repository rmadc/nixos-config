# The standard agent plus the tools our pipeline needs.
FROM jenkins/inbound-agent:3396.ve02b_5cde31b_2-5-jdk21

# Installing packages needs root.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends shellcheck python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/tools \
    && /opt/tools/bin/pip install --no-cache-dir ruff pytest \
    && ln -s /opt/tools/bin/ruff /opt/tools/bin/pytest /usr/local/bin/

# Run builds as the unprivileged user again.
USER jenkins