import sys
import time
import shutil
from pathlib import Path

def main() -> int:
    if len(sys.argv) < 3:
        return 1

    new_exe = Path(sys.argv[1]).resolve()
    target = Path(sys.argv[2]).resolve()
    log_file = target.parent / "forge-update.log"

    def log(msg: str):
        log_file.write_text(
            (log_file.read_text(encoding="utf-8", errors="ignore") if log_file.exists() else "") + msg + "\n",
            encoding="utf-8",
            errors="ignore",
        )

    log(f"[Updater] new_exe={new_exe}")
    log(f"[Updater] target={target}")

    for _ in range(200):
        try:
            bak = target.with_suffix(".exe.bak")
            if bak.exists():
                bak.unlink()

            if target.exists():
                shutil.move(str(target), str(bak))

            shutil.move(str(new_exe), str(target))
            log("[Updater] Updated successfully")
            return 0

        except PermissionError:
            time.sleep(0.25)
        except Exception as e:
            log(f"[Updater] Failed: {type(e).__name__}: {e}")
            return 1

    log("[Updater] Timed out waiting for Forge to exit")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
