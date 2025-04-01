# Install project dependencies
dep:
    pip install -r requirements.txt

local:
    python3 local.py

dev:
    uvicorn serve:app --reload

# Pre-commit quality checks
pre-commit: dep
    black .
    ruff check . --show-source