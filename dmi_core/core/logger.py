from datetime import datetime
from pathlib import Path


def get_logger(engine_name: str):
    log_dir = Path("F:/Python/DMI_CORE_V1.0/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}.log"

    def log(message: str, level: str = "INFO"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{now}] [{level}] [{engine_name}] {message}"

        print(line)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    return log