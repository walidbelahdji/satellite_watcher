ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION}
ARG DEMO_PORT=8501

WORKDIR /app

COPY requirements.txt requirements-demo.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt -r requirements-demo.txt

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

COPY config/demo.env .env
COPY config/demo.env config/demo.env
EXPOSE ${DEMO_PORT}
ENTRYPOINT ["python", "-m", "detectorLitter.demo"]
