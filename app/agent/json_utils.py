import json


def extract_json_object(raw: str) -> dict:
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Model response does not contain a JSON object")
    payload = json.loads(raw[start : end + 1])
    if not isinstance(payload, dict):
        raise TypeError("Model response must decode to a JSON object")
    return payload
