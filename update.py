import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
import requests

GITHUB_OWNER = "ridit-jangra"
GITHUB_REPO = "Forge"
ASSET_NAME = "forge.exe"

API_LATEST = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

UPDATER_SCRIPT = r"""
import os
import sys
import time
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("[Update] Usage: forge-updater <downloaded_exe> <target_exe>")
        return 1

    downloaded = Path(sys.argv[1]).resolve()
    target = Path(sys.argv[2]).resolve()

    for _ in range(60):
        try:
            if target.exists():
                backup = target.with_suffix(".exe.bak")
                try:
                    if backup.exists():
                        backup.unlink()
                except:
                    pass

                shutil.move(str(target), str(backup))
            shutil.move(str(downloaded), str(target))
            print("[Update] Updated successfully!")
            return 0
        except PermissionError:
            time.sleep(0.2)
        except Exception as e:
            print(f"[Update] Failed: {e}")
            return 1

    print("[Update] Timed out waiting for Forge to exit.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
"""

def _download(url: str, out_path: Path) -> None:
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length") or 0)
        got = 0
        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                got += len(chunk)
                if total:
                    pct = int(got * 100 / total)
                    print(f"\r[Update] Downloading... {pct}%", end="")
        print()

def _latest_asset_url() -> str:
    r = requests.get(API_LATEST, timeout=20)
    r.raise_for_status()
    data = r.json()
    assets = data.get("assets") or []
    for a in assets:
        if (a.get("name") or "").lower() == ASSET_NAME.lower():
            return a.get("browser_download_url") or ""
    raise RuntimeError(f"Release asset '{ASSET_NAME}' not found in latest release.")

def run_update() -> None:
    if not sys.platform.startswith("win"):
        print("[Update] Currently only Windows self-update is supported.")
        return

    try:
        url = _latest_asset_url()
    except Exception as e:
        print(f"[Update] Failed to get latest release: {e}")
        return

    tmp_dir = Path(tempfile.mkdtemp(prefix="forge_update_"))
    downloaded = tmp_dir / ASSET_NAME
    updater_py = tmp_dir / "forge-updater.py"

    try:
        print(f"[Update] Latest release asset: {url}")
        _download(url, downloaded)

        updater_py.write_text(UPDATER_SCRIPT, encoding="utf-8")

        target_exe = Path(sys.executable).resolve()
        
        print("[Update] Target exe:", Path(sys.executable).resolve())
        print("[Update] Temp exe:", downloaded.resolve())

        if target_exe.suffix.lower() != ".exe":
            print("[Update] You are not running from a .exe build. Build/install Forge EXE first.")
            return

        print("[Update] Launching updater...")
        subprocess.Popen(
            [sys.executable, str(updater_py), str(downloaded), str(target_exe)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        print("[Update] Close this Forge window to finish updating.")
        sys.exit(0)

    except Exception as e:
        print(f"[Update] Update failed: {e}")
