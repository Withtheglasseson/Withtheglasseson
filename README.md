# SUA Hybrid Python Version

This repository contains a runnable scaffold for the SUA Hybrid Python system. The structure mirrors the intended project layout and provides placeholder components with a FastAPI entry point.

## Structure

- `main.py`: FastAPI app wiring together the brains and database.
- `database.py`: SQLite helper for storing triage decisions (also initializes schema).
- `models.py`: Shared dataclass models.
- `utils/`: Supporting modules for APIs, market analysis, triage, and calibration.
- `config.yaml`: YAML configuration stub.
- `requirements.txt`: Python dependencies.

## Usage

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 database.py
python3 -m uvicorn main:app --reload
```

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"context": {"region": "NA"}}'
```
