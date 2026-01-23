- 👋 Hi, I’m @Withtheglasseson
- 👀 I’m interested in ...
- 🌱 I’m currently learning ...
- 💞️ I’m looking to collaborate on ...
- 📫 How to reach me ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...

## System Structure

```json
{
  "brains": ["market_brain", "triage_brain", "calibration_brain"],
  "database": "local (SQLite)",
  "data_exchange": "JSON or CSV via upload/download",
  "purpose": "Assist with predictive pricing, diagnostics, and drift analysis"
}
```

## Local Development

```bash
cd auction_underwriter
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

<!---
Withtheglasseson/Withtheglasseson is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
