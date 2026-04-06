FROM python:3.12-slim

WORKDIR /app

# Enable BuildKit cache mounts for pip and Poetry
ENV PIP_NO_CACHE_DIR=1 \
    POETRY_CACHE_DIR=/root/.cache/pypoetry

# Install Poetry with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    pip install --upgrade pip && \
    pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies with cache mounts
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy source code
COPY . .

CMD ["poetry", "run", "start"]



