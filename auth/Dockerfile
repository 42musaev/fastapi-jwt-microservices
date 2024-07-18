FROM python:3.12-alpine
RUN apk add --no-cache gcc musl-dev libffi-dev
RUN pip install --no-cache-dir poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
COPY . .
