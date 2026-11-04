# Build context: repository root. Fieldkit binds this image to container workshop.
FROM ubuntu:24.04
ARG TARGETARCH
ARG CODE_SERVER_VERSION=4.144.0
ARG TEMPORAL_CLI_VERSION=1.9.1
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      bash ca-certificates curl python3 python3-venv tini \
    && rm -rf /var/lib/apt/lists/*
RUN arch="${TARGETARCH:-$(dpkg --print-architecture)}" \
    && curl --fail --silent --show-error --location --retry 3 \
      "https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server_${CODE_SERVER_VERSION}_${arch}.deb" -o /tmp/code-server.deb \
    && apt-get update && apt-get install -y --no-install-recommends /tmp/code-server.deb \
    && rm -rf /var/lib/apt/lists/* /tmp/code-server.deb \
    && curl --fail --silent --show-error --location --retry 3 \
      "https://github.com/temporalio/cli/releases/download/v${TEMPORAL_CLI_VERSION}/temporal_cli_${TEMPORAL_CLI_VERSION}_linux_${arch}.tar.gz" -o /tmp/temporal.tar.gz \
    && tar -xzf /tmp/temporal.tar.gz -C /usr/local/bin temporal \
    && rm /tmp/temporal.tar.gz
COPY requirements.txt /opt/preflight/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r /opt/preflight/requirements.txt
COPY app/ /opt/preflight/
COPY instruqt/docker/start.sh instruqt/docker/terminal.sh /opt/preflight/bin/
RUN chmod +x /opt/preflight/bin/*.sh
ENV PATH="/opt/venv/bin:${PATH}"
WORKDIR /root
EXPOSE 5000 8080 8090 8092 8233
ENTRYPOINT ["/usr/bin/tini", "--"]
# Lifecycle setup starts services. PID 1 stays alive if one fails so instructors
# can still reach the native terminal and logs.
CMD ["sleep", "infinity"]
