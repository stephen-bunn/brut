# base used for version independency
FROM python:3.9-alpine

# fetch build dependent packages
RUN apk add --no-cache curl gcc g++ make linux-headers musl-dev openssl-dev libffi-dev file rust cargo

    # python
ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    POETRY_VERSION=1.1.5 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# prepend peotry and venv to path
ENV PATH="$POETRY_HOME/bin:/code/.venv/bin:$PATH" \
    PYTHONPATH="/code/src:$PYTHONPATH"

# setup dependency management (uses $POETRY_VERSION and $POETRY_HOME)
RUN pip install "poetry==$POETRY_VERSION"

# copy requirements definitions to ensure they are cached
WORKDIR /code
COPY pyproject.toml poetry.lock /code

# install runtime dependencies (uses $POETRY_VIRTUALENVS_IN_PROJECT)
RUN poetry install --no-dev --no-root

COPY . /code
CMD ["/code/docker/worker-entrypoint.sh"]
