# carecompanion-ai 🩺

A patient-facing web app built to **showcase interest in medicine combined with AI**, designed for an MD application portfolio. It demonstrates how thoughtful, safety-first software can support patients — while making clear that technology never replaces a clinician.

The app pairs a **trained machine-learning model** with **live open-source medical data**: a scikit-learn classifier ranks probable conditions from your symptoms, and each result is enriched with authoritative reference material fetched from the open Wikipedia REST API. No API keys are required, and no personal or patient data ever leaves your device — only a condition name is used to look up public reference material.

## ✨ Features

| Feature | Description |
| --- | --- |
| 🔍 **AI Symptom Checker** | A scikit-learn model ranks probable conditions with calibrated probabilities, red-flag emergency detection, and open-data reference summaries. |
| 💬 **Health Assistant** | A conversational helper for general wellness questions. Uses **OpenAI** when an API key is configured, and falls back to an offline rule-based assistant otherwise. Emergencies are always escalated. |
| 💡 **Wellness Library** | A rotating "tip of the day" plus a catalogue of evidence-informed daily habits. |

Patient safety is built in: prominent disclaimers, emergency red-flag detection, and language that always points back to licensed clinicians.

## 🧠 How the AI Works

1. **Knowledge base** — a curated dataset of 19 common conditions and their symptoms lives in `data/disease_symptoms.csv` (61-symptom vocabulary).
2. **ML model** — `ai/ml_model.py` synthesises realistic "patients" from the knowledge base and trains a **Bernoulli Naive Bayes** classifier (scikit-learn). Reported symptoms are turned into a binary feature vector and the model returns a ranked differential with `predict_proba` probabilities.
3. **Open-data enrichment** — `ai/open_data.py` fetches concise, authoritative summaries for the top conditions from the **Wikipedia REST API** (open data, no key). If the network is unavailable, it falls back to the local knowledge base so the app still works offline.
4. **Safety layer** — `ai/symptom_checker.py` always runs hard-coded red-flag rules (e.g. chest pain, slurred speech) that override the model and recommend emergency care.

## 🧱 Tech Stack

- **Backend:** Python + Flask
- **Machine learning:** scikit-learn (Bernoulli Naive Bayes), NumPy
- **Open data:** Wikipedia REST API via `requests`
- **LLM (optional):** OpenAI (`gpt-4o-mini` by default) with graceful offline fallback
- **Frontend:** HTML, CSS, vanilla JavaScript (no build step)

## 📁 Project Structure

```
md-ai-showcase/
├── app.py                    # Flask app + API routes
├── requirements.txt
├── data/
│   └── disease_symptoms.csv  # Open knowledge base (conditions ↔ symptoms)
├── ai/                       # AI package
│   ├── knowledge_base.py     # Loads dataset + symptom vocabulary
│   ├── ml_model.py           # scikit-learn diagnosis model
│   ├── open_data.py          # Wikipedia REST API enrichment
│   ├── symptom_checker.py    # ML + red-flag safety + enrichment
│   ├── assistant.py          # Intent-based health chat (offline)
│   ├── llm_assistant.py      # Optional OpenAI-powered chat
│   └── health_tips.py        # Daily wellness tips
├── templates/
│   └── index.html            # Single-page UI
└── static/
    ├── css/style.css
    └── js/main.js
```

## 🚀 Getting Started

From the project folder:

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### 🤖 Enable the OpenAI assistant (optional)

The chat assistant works offline out of the box. To use a real LLM instead:

```powershell
# Copy the template and add your key
Copy-Item .env.example .env
# Then edit .env and set OPENAI_API_KEY=sk-...
```

On the next `python app.py`, the assistant automatically switches to OpenAI
(model configurable via `OPENAI_MODEL`, default `gpt-4o-mini`). The `.env` file is
git-ignored, and if the key is missing or a request fails, the app silently falls
back to the offline rule-based assistant. A safety pre-filter always handles
emergency messages locally, before any API call.

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET`  | `/` | The web app |
| `GET`  | `/api/symptoms` | The symptom vocabulary the model understands |
| `POST` | `/api/symptom-check` | Body: `{ "symptoms": ["fever", "cough"] }` → ML differential + enrichment |
| `POST` | `/api/chat` | Body: `{ "message": "how much sleep do I need?" }` (OpenAI or rule-based) |
| `GET`  | `/api/assistant-mode` | Reports whether the OpenAI assistant is active |
| `GET`  | `/api/health-tips` | Full tip catalogue |
| `GET`  | `/api/health` | Liveness check |

## ⚠️ Important Disclaimer

CareCompanion is an **educational demonstration only**. The machine-learning model is trained on a small, synthesised dataset for illustration and is **not** clinically validated. It does **not** provide medical diagnosis or treatment and must not be used for real medical decisions. Always consult a licensed clinician. In an emergency, call your local emergency number.

## 🧭 Why This Project

This project reflects a genuine interest in medicine and a belief that AI, used responsibly, can make healthcare more accessible and patient-centered — with safety, transparency, and the clinician relationship always at the core.
