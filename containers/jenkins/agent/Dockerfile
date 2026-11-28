# The standard agent plus the tools our pipeline needs.
FROM jenkins/inbound-agent:3396.ve02b_5cde31b_2-5-jdk21

# Installing packages needs root.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends shellcheck \
    && rm -rf /var/lib/apt/lists/*

# Run builds as the unprivileged user again.
USER jenkins