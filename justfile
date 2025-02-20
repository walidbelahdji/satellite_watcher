dep:
    pip install -r requirements.txt

local:
    python3 local.py
dev:
    uvicorn serve:app --reload