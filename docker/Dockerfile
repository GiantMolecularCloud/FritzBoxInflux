# The image is built in two stages with caching to allow faster built times and
# smaller image sizes. The first stage installs the dependencies and the second
# stage installs the project itself. This way the slow dependencies
# installation is only done when the dependencies change but not when the
# project source files change.


############################################################
# Stage 1: Build environment

FROM python:3.13-slim as builder

ARG POETRY_VERSION=2.1

RUN pip install "poetry==${POETRY_VERSION}"

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /fritzbox_influx

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root


############################################################
# Stage 2: Install project on existing environment

FROM python:3.13-slim as runtime

ENV VIRTUAL_ENV=/fritzbox_influx/.venv \
    PATH="/fritzbox_influx/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src /fritzbox_influx/

ENTRYPOINT ["python", "-m", "fritzbox_influx.entrypoint"]
