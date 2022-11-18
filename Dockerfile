FROM continuumio/miniconda3:4.10.3

# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

COPY . /app/
WORKDIR /app
RUN conda env update -n base -f conda-env.yaml

CMD ["python", "src/server.py"]