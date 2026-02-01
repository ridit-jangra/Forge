import os
from pathlib import Path

FOLDER_NAME = ".forge"
FOLDER_PATH = f"./{FOLDER_NAME}"

SERVER_URL = os.getenv("FORGE_SERVER_URL", "https://vault.ridit.space")
USER_SESSION_FILE = (Path.home() / os.getenv("FORGE_SESSION", ".forge_session")).expanduser()

DEFAULT_TIMEOUT = 20
