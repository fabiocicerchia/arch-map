# arch-map is a stdlib-only Python CLI. This image installs it and runs it as
# a non-root user. Note: to read live clusters you must also provide `kubectl`
# (and a kubeconfig) at runtime — this base image ships neither.
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir . && adduser --disabled-password --uid 10001 app
USER app

# One-shot CLI tool, not a service — this just confirms the interpreter starts.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=1 \
    CMD python3 -c "import sys; sys.exit(0)"

ENTRYPOINT ["arch-map"]
