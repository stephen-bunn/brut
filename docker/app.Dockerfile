# base used for version independency
FROM python:3.9-alpine

# fetch build dependent packages
RUN apk add --no-cache curl gcc g++ make linux-headers musl-dev openssl-dev libffi-dev file rust cargo git libxml2-dev libxslt-dev

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
    POETRY_NO_INTERACTION=1 \
    # megu
    MEGU_PLUGIN_DIR=/.megu/plugins \
    MEGU_LOG_DIR=/code/data/logs

# prepend peotry and venv to path
ENV PATH="$POETRY_HOME/bin:/code/.venv/bin:$PATH" \
    PYTHONPATH="/code/src:$PYTHONPATH"

# setup dependency management (uses $POETRY_VERSION and $POETRY_HOME)
RUN pip install "poetry==$POETRY_VERSION"

# copy requirements definitions to ensure they are cached
WORKDIR /code
COPY pyproject.toml poetry.lock /code/

# install runtime dependencies (uses $POETRY_VIRTUALENVS_IN_PROJECT)
RUN poetry install --no-dev --no-root

# install and setup public megu plugins
RUN mkdir -p $MEGU_PLUGIN_DIR/megu_gfycat
RUN python -m pip install --upgrade git+https://github.com/stephen-bunn/megu-gfycat.git --target $MEGU_PLUGIN_DIR/megu_gfycat

COPY ./vendor /vendor
COPY ./scripts /scripts
RUN /scripts/install-vendors.sh

COPY . /code/
RUN mkdir -p /data/
CMD ["/code/docker/app-entrypoint.sh"]
