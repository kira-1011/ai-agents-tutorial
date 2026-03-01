import json


def extract_json_from_response(response: str) -> dict | None:
    response = response.strip()
    if response.startswith("```"):
        response = response.split("\n", 1)[1]
    if response.endswith("```"):
        response = response[:-3]
    response = response.strip()
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # handle single quotes from LLM (e.g. {'key': 'value'})
        try:
            return json.loads(response.replace("'", '"'))
        except json.JSONDecodeError:
            return None
