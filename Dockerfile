FROM python:3.11-slim
RUN apt-get -y update && apt-get -y install curl
WORKDIR /code
COPY requirements/prod.txt requirements.txt
COPY requirements/common.txt common.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt -r common.txt 
# Download latest model
ADD https://spring-ai-datasets.s3.eu-west-3.amazonaws.com/model.onnx model.onnx
COPY /src .
# nosemgrep
HEALTHCHECK --interval=10s --timeout=10s --start-period=3s --retries=3 CMD curl -f http://localhost:8080/health
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8080"]
