FROM python:3.12-slim AS builder

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.3

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove --purge -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./../pyproject.toml ./../poetry.lock /app/
RUN poetry install --only main, frontend --no-root \
    && rm -rf $POETRY_CACHE_DIR

FROM python:3.11-slim AS final

WORKDIR /app
COPY --from=builder /app /app

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]