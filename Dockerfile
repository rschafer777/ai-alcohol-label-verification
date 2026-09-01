FROM node:24.14.0-alpine@sha256:7fddd9ddeae8196abf4a3ef2de34e11f7b1a722119f91f28ddf1e99dcafdf114 AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12.10-slim-bookworm@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db AS python-build
COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY ops/fetch_models.py ops/model-manifest.json ops/
RUN /app/.venv/bin/python ops/fetch_models.py models

FROM python:3.12.10-slim-bookworm@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db AS runtime
ADD --checksum=sha256:48fec46bda7f5b1638b9e959889bfbc20491247d402d120bb152687eb48143d7 \
    https://deb.debian.org/debian/pool/main/g/gcc-12/libgomp1_12.2.0-14+deb12u1_amd64.deb \
    /tmp/libgomp1.deb
RUN dpkg -i /tmp/libgomp1.deb \
    && rm /tmp/libgomp1.deb \
    && groupadd --system --gid 10001 labelverify \
    && useradd --system --uid 10001 --gid labelverify --home-dir /app labelverify

ARG LABELVERIFY_BUILD_ID
RUN test -n "$LABELVERIFY_BUILD_ID"

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/backend \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LABELVERIFY_RUNTIME_MODE=production \
    LABELVERIFY_MODEL_ROOT=/app/models \
    LABELVERIFY_SPOOL_ROOT=/tmp/labelverify-spool \
    LABELVERIFY_SAMPLE_MANIFEST=/app/fixtures/sample/sample-manifest-v1.json \
    LABELVERIFY_STATIC_ROOT=/app/frontend/dist \
    LABELVERIFY_BUILD_ID=$LABELVERIFY_BUILD_ID

COPY --from=python-build /app/.venv /app/.venv
COPY --from=python-build /app/models /app/models
COPY backend/ backend/
COPY contracts/ contracts/
COPY fixtures/sample/ fixtures/sample/
COPY --from=frontend-build /build/frontend/dist frontend/dist/

RUN chmod -R a-w /app/models \
    && mkdir -p /tmp/labelverify-spool \
    && chown labelverify:labelverify /tmp/labelverify-spool
USER 10001:10001

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; r=urllib.request.Request('http://127.0.0.1:8080/health/ready',headers={'Host':os.environ['LABELVERIFY_ALLOWED_HOST']}); urllib.request.urlopen(r,timeout=2)"

CMD ["uvicorn", "labelverify.api.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--no-access-log"]
