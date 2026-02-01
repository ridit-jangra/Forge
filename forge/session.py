import json
import datetime
from .config import USER_SESSION_FILE

def save_user_session(user_data: dict, token: str) -> None:
    session_data = {
        "user": user_data,
        "token": token,
        "logged_in_at": datetime.datetime.now().isoformat()
    }
    USER_SESSION_FILE.write_text(json.dumps(session_data, indent=2), encoding="utf-8")
    print("[Local] Session saved")

def load_user_session() -> dict | None:
    if not USER_SESSION_FILE.exists():
        return None
    try:
        return json.loads(USER_SESSION_FILE.read_text(encoding="utf-8"))
    except:
        return None

def clear_user_session() -> None:
    if USER_SESSION_FILE.exists():
        USER_SESSION_FILE.unlink()
        print("[Local] Session cleared")

def get_auth_headers() -> dict:
    session = load_user_session()
    if not session:
        return {}
    return {"Authorization": f"Bearer {session['token']}"}
