import requests

def safe_json(resp: requests.Response):
    ct = (resp.headers.get("content-type") or "").lower()
    if resp.status_code >= 400:
        raise Exception(f"{resp.status_code} {(resp.text or '')[:300]}")
    if "application/json" not in ct:
        raise Exception(f"Non-JSON response ({ct}): {(resp.text or '')[:300]}")
    try:
        return resp.json()
    except Exception:
        raise Exception(f"Invalid JSON: {(resp.text or '')[:300]}")
