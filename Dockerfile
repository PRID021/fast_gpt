# 
FROM python:3.11-buster AS builder

# 
WORKDIR /server

# 
COPY ./requirements.txt /server/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

# 
COPY ./app /server/app

# 
FROM builder AS development
WORKDIR /server/app
ENV ENVIRONMENT=development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080","--reload"]