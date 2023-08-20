FROM python:3.11-slim-buster

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --only main --no-root --no-directory

COPY . .

RUN poetry install --only main

ENTRYPOINT ["poetry", "run", "python", "-m", "vans_bot"]
