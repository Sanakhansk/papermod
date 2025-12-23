import json

def load_persona(json_path):
    import json

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    persona = data.get("persona", {}).get("role", "").strip()
    job = data.get("job_to_be_done", {}).get("task", "").strip()

    if not persona or not job:
        raise ValueError("Persona or job_to_be_done is missing or malformed")

    return {
        "persona": persona,
        "job_to_be_done": job
    }

