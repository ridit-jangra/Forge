import getpass
import requests
from ..config import SERVER_URL, DEFAULT_TIMEOUT
from ..session import save_user_session, clear_user_session, load_user_session

def register_user() -> None:
    print("=== Forge Registration ===")
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("[Error] Passwords don't match")
        return
    if len(password) < 6:
        print("[Error] Password must be at least 6 characters")
        return

    try:
        r = requests.post(
            f"{SERVER_URL}/api/auth/register/initiate",
            json={"username": username, "email": email, "password": password},
            timeout=DEFAULT_TIMEOUT
        )
        if r.status_code != 200:
            try:
                print("[Error]", r.json().get("detail", "Registration failed"))
            except:
                print("[Error]", r.text[:200])
            return

        print(f"[Success] Verification email sent to {email}")
        otp = input("Enter OTP: ").strip()

        r = requests.post(
            f"{SERVER_URL}/api/auth/register/verify",
            json={"email": email, "otp": otp},
            timeout=DEFAULT_TIMEOUT
        )
        if r.status_code != 200:
            try:
                print("[Error]", r.json().get("detail", "Verification failed"))
            except:
                print("[Error]", r.text[:200])
            return

        data = r.json()
        user = data.get("user")
        token = data.get("token")
        save_user_session(user, token)
        print(f"[Success] Logged in as {user['username']}")
    except Exception as e:
        print("[Error]", e)

def login_user() -> None:
    print("=== Forge Login ===")
    username = input("Enter username or email: ").strip()
    password = getpass.getpass("Enter password: ")

    try:
        r = requests.post(
            f"{SERVER_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=DEFAULT_TIMEOUT
        )
        if r.status_code != 200:
            print("[Error]", r.json().get("detail", "Login failed"))
            return

        token = r.json().get("token")
        me = requests.get(f"{SERVER_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=DEFAULT_TIMEOUT)
        if me.status_code != 200:
            print("[Error] Failed to get user info")
            return
        user = me.json().get("user")
        save_user_session(user, token)
        print(f"[Success] Logged in as {user['username']}")
    except Exception as e:
        print("[Error]", e)

def logout_user() -> None:
    s = load_user_session()
    if not s:
        print("[Info] No active session")
        return
    name = s["user"]["username"]
    clear_user_session()
    print(f"[Success] Logged out {name}")

def whoami() -> None:
    s = load_user_session()
    if not s:
        print("Not logged in")
        return
    u = s["user"]
    print(f"Logged in as: {u.get('username')}")
    print(f"User ID: {u.get('id')}")
    if "email" in u:
        print(f"Email: {u.get('email')}")
