# We are using mutli-stage builds as both the app and workers need the same image
# https://docs.docker.com/build/building/multi-stage/
FROM python:3.10-alpine as build

ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install the packaged dependnecies
COPY pyproject.toml poetry.lock /
RUN poetry install --no-dev --no-root

# Install the vendored dependencies
COPY ./vendor /vendor/
COPY ./scripts /scripts/
RUN mkdir -p /megu/
ENV BRUT_MEGU_PLUGIN_DIR=/megu/
RUN /scripts/install-vendors.sh

COPY ./src /code/
COPY brut.yaml /
RUN mkdir -p /data/
ENV PYTHONPATH="/code/:$PYTHONPATH" \
    BRUT_CONFIG_PATH=/brut.yaml \
    BRUT_STORE_DIR=/data/ \
    BRUT_DATABASE_PATH=/data/brut.db \
    BRUT_REDIS_URL=redis://redis:6379/0

# Build application using custom entrypoint
FROM build as app
CMD ["/scripts/app-entrypoint.sh"]

# Build worker using custom entrypoint
FROM build as worker
CMD ["/scripts/worker-entrypoint.sh"]
