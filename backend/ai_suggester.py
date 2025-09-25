import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# Try these public, free text2text models in order.
MODEL_CANDIDATES = [
    "google/flan-t5-base",
    "google/flan-t5-small",
]

MAX_CHARS = 4000
MAX_NEW_TOKENS = 180

def _clean(s: str) -> str:
    s = (s or "").strip()
    return s[:MAX_CHARS]

def _post(model_id: str, payload: dict, retries: int = 3) -> requests.Response:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    backoff = 2.0
    last = None
    for i in range(retries):
        r = requests.post(url, headers=HEADERS, json=payload, timeout=60)
        if r.status_code == 200:
            return r
        # Free tier often returns 503 (loading) or 429 (rate limit) – backoff and retry
        if r.status_code in (429, 503):
            time.sleep(backoff * (i + 1))
            last = r
            continue
        # For other codes, return immediately
        return r
    return last or r

def _call_hf_with_fallback(payload: dict) -> str:
    if not HF_TOKEN:
        raise RuntimeError("Missing HUGGINGFACEHUB_API_TOKEN in backend/.env")

    errors = []
    for model in MODEL_CANDIDATES:
        r = _post(model, payload)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return (data[0].get("generated_text") or "").strip()
            # some models return {"generated_text": "..."} directly
            if isinstance(data, dict) and "generated_text" in data:
                return (data["generated_text"] or "").strip()
            errors.append(f"{model}: unexpected payload {str(data)[:160]}")
            continue

        if r.status_code == 404:
            errors.append(f"{model}: 404 (model not found)")
            continue
        if r.status_code in (401, 403):
            raise RuntimeError(f"AUTH_ERROR {r.status_code}: {r.text[:200]}")
        if r.status_code in (429, 503):
            errors.append(f"{model}: {r.status_code} (loading/rate limit)")
            continue

        errors.append(f"{model}: {r.status_code} {r.text[:160]}")
        continue

    raise RuntimeError("HF fallback failed: " + " | ".join(errors))

def get_resume_suggestions(resume_text: str, jd_text: str) -> str:
    resume_text = _clean(resume_text)
    jd_text = _clean(jd_text)

    prompt = (
        "You are an ATS and hiring expert. Given the Resume and Job Description, "
        "write exactly 3 short, actionable bullet-point suggestions to improve the resume. "
        "Be specific, focus on keywords, measurable results, and structure. "
        "Output only the three bullets, one per line, no extra commentary.\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{jd_text}\n\n"
        "Suggestions:\n"
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": 0.5,
            "return_full_text": False
        }
    }

    try:
        text = _call_hf_with_fallback(payload)
    except Exception as e:
        # Safe default if HF is unavailable
        return (
            "- Add role-specific keywords from the JD\n"
            "- Quantify achievements with numbers/percentages\n"
            "- Improve section headings and bullet clarity"
        )

    return text or (
        "- Add role-specific keywords from the JD\n"
        "- Quantify achievements with numbers/percentages\n"
        "- Improve section headings and bullet clarity"
    )