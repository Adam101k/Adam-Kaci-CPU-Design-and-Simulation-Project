# BEGIN-AI
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (../.. from tools/)
INCLUDE_EXTS = {
    ".py", ".md", ".yml", ".yaml", ".toml", ".json",
    ".txt", ".cfg", ".ini"
}
EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".idea", ".vscode", "build", "dist"}

def iter_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in INCLUDE_EXTS or p.name in ("Makefile", "Dockerfile"):
            yield p

def count_ai_lines():
    total = 0
    ai_tagged = 0

    for path in iter_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        total += len(lines)

        in_ai_block = False
        for line in lines:
            s = line.strip()
            if "AI-BEGIN" in s:
                in_ai_block = True
            # Count the line if we’re currently inside an AI block
            if in_ai_block:
                ai_tagged += 1
            if "AI-END" in s and in_ai_block:
                in_ai_block = False

    return total, ai_tagged

def main():
    total, ai_tagged = count_ai_lines()
    percent = (100.0 * ai_tagged / total) if total else 0.0
    report = {
        "total_lines": total,
        "ai_tagged_lines": ai_tagged,
        "percent": round(percent, 1),
        "tools": ["ChatGPT"],
        "method": "count markers"
    }
    out = ROOT / "ai_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}:\n{json.dumps(report, indent=2)}")

if __name__ == "__main__":
    main()

# END-AI