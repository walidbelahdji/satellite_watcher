ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION}
ARG API_PORT=8080

RUN apt-get update \
    && apt-get install --no-install-recommends -y libxcb1 libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

# Runtime defaults and model source are maintained outside the image recipe.
COPY config/server.env .env
COPY config/server.env config/server.env
COPY config/model.env config/model.env
COPY scripts/download_model.py scripts/download_model.py
RUN python scripts/download_model.py --config config/model.env

COPY docker/healthcheck.py docker/healthcheck.py
EXPOSE ${API_PORT}
HEALTHCHECK --interval=10s --timeout=10s --start-period=3s --retries=3 \
    CMD ["python", "docker/healthcheck.py"]

CMD ["python", "-m", "detectorLitter"]
