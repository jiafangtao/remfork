FROM python:3.9-alpine

WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY src .

RUN pip install pipenv && \
    pipenv install --system --deploy

CMD ["/usr/local/bin/python3", "/app/main.py", "-h"]