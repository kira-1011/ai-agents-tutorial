import json


def extract_json_from_response(response: str) -> dict | None:
    response = response.strip()
    if response.startswith("```"):
        response = response.split("\n", 1)[1]
    if response.endswith("```"):
        response = response[:-3]
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return None
