import sys
import time
import tempfile
import subprocess
from pathlib import Path

import requests

GITHUB_OWNER = "ridit-jangra"
GITHUB_REPO = "Forge"

FORGE_ASSET = "forge.exe"
UPDATER_ASSET = "forge-updater.exe"

API_LATEST = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _download(url: str, out_path: Path) -> None:
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length") or 0)
        got = 0
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                got += len(chunk)
                if total:
                    pct = int(got * 100 / total)
                    print(f"\r[Update] Downloading {out_path.name}... {pct}%", end="")
        print()


def _latest_assets() -> dict:
    r = requests.get(
        API_LATEST,
        timeout=20,
        headers={"Accept": "application/vnd.github+json"},
    )
    r.raise_for_status()
    data = r.json()

    assets = data.get("assets") or []
    by_name = {}
    for a in assets:
        name = (a.get("name") or "").strip()
        url = (a.get("browser_download_url") or "").strip()
        if name and url:
            by_name[name.lower()] = url

    return by_name


def run_update() -> None:
    if not sys.platform.startswith("win"):
        print("[Update] Self-update is currently only supported on Windows.")
        return

    try:
        assets = _latest_assets()
        forge_url = assets.get(FORGE_ASSET.lower())
        updater_url = assets.get(UPDATER_ASSET.lower())

        if not forge_url:
            print(f"[Update] Latest release does not contain '{FORGE_ASSET}'.")
            return
        if not updater_url:
            print(f"[Update] Latest release does not contain '{UPDATER_ASSET}'.")
            return

    except Exception as e:
        print(f"[Update] Failed to fetch latest release: {e}")
        return

    tmp_dir = Path(tempfile.mkdtemp(prefix="forge_update_")).resolve()
    downloaded_forge = (tmp_dir / "forge.new.exe").resolve()
    downloaded_updater = (tmp_dir / UPDATER_ASSET).resolve()

    try:
        print(f"[Update] Downloading: {FORGE_ASSET}")
        _download(forge_url, downloaded_forge)

        print(f"[Update] Downloading: {UPDATER_ASSET}")
        _download(updater_url, downloaded_updater)

        target_exe = Path(sys.executable).resolve()
        print("[Update] Target exe:", target_exe)
        print("[Update] Temp forge:", downloaded_forge)
        print("[Update] Temp updater:", downloaded_updater)

        if target_exe.suffix.lower() != ".exe":
            print("[Update] You are not running from a .exe build.")
            print("[Update] Build/install Forge EXE first.")
            return

        if not downloaded_updater.exists():
            print("[Update] Updater download missing.")
            return

        print("[Update] Launching updater...")
        subprocess.Popen(
            [str(downloaded_updater), str(downloaded_forge), str(target_exe)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=str(target_exe.parent),
        )

        print("[Update] Close this Forge window to finish updating.")
        sys.exit(0)

    except Exception as e:
        print(f"[Update] Update failed: {e}")
