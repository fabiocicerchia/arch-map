# arch-map is a stdlib-only Python CLI. This image installs it and runs it as
# a non-root user. Note: to read live clusters you must also provide `kubectl`
# (and a kubeconfig) at runtime — this base image ships neither.
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir . && adduser --disabled-password --uid 10001 app
USER app

ENTRYPOINT ["arch-map"]
