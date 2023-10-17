FROM python:3.11-alpine3.18

RUN apk add --no-cache bash gcc libffi-dev libc-dev

# python
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=300

COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]
