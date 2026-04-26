# syntax=docker/dockerfile:1.7

ARG RUST_VERSION=1.88
ARG PYTHON_VERSION=3.11
ARG TYPST_VERSION=0.14.2

FROM docker.io/library/rust:${RUST_VERSION}-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/rust_api/Cargo.toml backend/rust_api/Cargo.lock backend/rust_api/build.rs ./backend/rust_api/
COPY backend/rust_api/src/main.rs backend/rust_api/src/lib.rs ./backend/rust_api/src/
WORKDIR /build/backend/rust_api
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    cargo fetch --locked

COPY backend/rust_api/src ./backend/rust_api/src

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/build/backend/rust_api/target \
    cargo build --release --locked \
    && mkdir -p /out \
    && cp /build/backend/rust_api/target/release/rust_api /out/rust_api

FROM docker.io/library/debian:bookworm-slim AS typst

ARG TYPST_VERSION
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    xz-utils \
    && rm -rf /var/lib/apt/lists/* \
    && case "${TARGETARCH:-amd64}" in \
      amd64) typst_target="x86_64-unknown-linux-musl" ;; \
      arm64) typst_target="aarch64-unknown-linux-musl" ;; \
      *) echo "unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL \
      "https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-${typst_target}.tar.xz" \
      -o /tmp/typst.tar.xz \
    && mkdir -p /tmp/typst \
    && tar -xJf /tmp/typst.tar.xz -C /tmp/typst --strip-components=1 \
    && install -m 0755 /tmp/typst/typst /usr/local/bin/typst \
    && /usr/local/bin/typst --version

FROM docker.io/library/python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_ROOT=/app \
    RUST_API_ROOT=/app/backend/rust_api \
    RUST_API_DATA_ROOT=/data \
    OUTPUT_ROOT=/data/jobs \
    PYTHON_BIN=python3 \
    TYPST_BIN=/usr/local/bin/typst \
    RETAIN_PDF_FONT_PATH=/usr/local/share/fonts/source-han-serif/SourceHanSerifSC-Regular.otf \
    RETAIN_PDF_TITLE_BOLD_FONT_PATH=/usr/local/share/fonts/source-han-serif/SourceHanSerifSC-Bold.otf \
    RETAIN_PDF_TYPST_FONT_FAMILY="Source Han Serif SC" \
    RUST_API_PORT=41000 \
    RUST_API_SIMPLE_PORT=42000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    fontconfig \
    fonts-noto-cjk \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=typst /usr/local/bin/typst /usr/local/bin/typst

RUN mkdir -p /usr/local/share/fonts/source-han-serif

COPY backend/fonts/SourceHanSerifSC-Regular.otf /usr/local/share/fonts/source-han-serif/SourceHanSerifSC-Regular.otf
COPY backend/fonts/SourceHanSerifSC-Bold.otf /usr/local/share/fonts/source-han-serif/SourceHanSerifSC-Bold.otf
COPY docker/fontconfig/65-source-han-serif-alias.conf /etc/fonts/conf.d/65-source-han-serif-alias.conf

RUN fc-scan /usr/local/share/fonts/source-han-serif/SourceHanSerifSC-Regular.otf >/dev/null \
    && fc-scan /usr/local/share/fonts/source-han-serif/SourceHanSerifSC-Bold.otf >/dev/null \
    && fc-cache -f

COPY docker/requirements-app.txt /tmp/requirements-app.txt
RUN pip install --no-cache-dir -r /tmp/requirements-app.txt

COPY --from=builder /out/rust_api /usr/local/bin/rust_api
COPY backend/scripts /app/backend/scripts
COPY backend/rust_api/auth.local.example.json /app/backend/rust_api/auth.local.example.json
COPY docker/entrypoint-app.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/backend/rust_api /app/backend/scripts /data/uploads /data/downloads /data/db /data/jobs

VOLUME ["/data"]

EXPOSE 41000 42000

ENTRYPOINT ["/entrypoint.sh"]
