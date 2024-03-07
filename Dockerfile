FROM python:3.11.3


WORKDIR /server

RUN pip install poetry==1.5.1

RUN poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root --no-directory

COPY . .

RUN poetry install --no-interaction --no-ansi


EXPOSE 8080

CMD exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --forwarded-allow-ips '*' && alembic upgrade head