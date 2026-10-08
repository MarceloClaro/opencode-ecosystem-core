import json
from pathlib import Path

processes = []
for directory in Path(r"\\wsl.localhost\Ubuntu\proc").iterdir():
    if not directory.name.isdigit():
        continue
    try:
        fields = dict(line.split(":", 1) for line in (directory / "status").read_text().splitlines() if ":" in line)
        processes.append({"pid": int(directory.name), "name": fields.get("Name", "").strip(),
                          "state": fields.get("State", "").strip(),
                          "rss_kb": int(fields.get("VmRSS", "0").strip().split()[0])})
    except (OSError, ValueError):
        continue
print(json.dumps(sorted(processes, key=lambda row: row["rss_kb"], reverse=True)[:12], indent=2))
