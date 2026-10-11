# Install or update project dependencies
dep:
    python3 -m pip install --upgrade -r requirements.txt
    python3 -m pip install --editable .

# Download the configured model artifact
model:
    python3 scripts/download_model.py

# Run detectorLitter dev server
dev:
    python3 -m detectorLitter --reload

# Run demo server
demo:
    python3 -m detectorLitter.demo

# Run docker compose
compose:
    docker-compose --profile demo up --build

# Bench a local server
bench:
    locust -f benchmarks/locustfile.py --headless --users 10 --run-time 60s -H http://localhost:8000 --html bench.html

# Run test suite against a local server
test:
    python3 -m tests.runner

# Update tests fixture
test-apply:
    python3 -m tests.runner --apply

# Pre-commit quality checks
pre-commit:
    black .
    ruff check . --show-source

# Deploy detectorLitter
deploy:
    fly deploy

# Deploy demo
deploy-demo:
    fly deploy -c demo.fly.toml --ha=false

# Deploy detectorLitter and demo
deploy-all: deploy deploy-demo
