"""One-off: rename Resonode → Audira.run across the repo."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", ".next", "__pycache__", ".pytest_cache", "postgres_data", "uploads"}
EXT = {
    ".py", ".ts", ".tsx", ".json", ".yml", ".yaml", ".md", ".xml", ".css",
    ".example", ".toml", ".txt", ".gitkeep", ".gitignore",
}

REPLACEMENTS = [
    ("resonode_core", "audira_core"),
    ("@resonode/", "@audira/"),
    ("resonode_session", "audira_session"),
    ('"name": "resonode"', '"name": "audira"'),
    ("Sign in to Resonode", "Sign in to Audira.run"),
    ("Resonode uses", "Audira.run uses"),
    ("Resonode orchestration", "Audira.run orchestration"),
    ("Resonode TRIBE", "Audira.run TRIBE"),
    ("Resonode RBAC", "Audira.run RBAC"),
    ("Resonode session", "Audira.run session"),
    ("Resonode JWT", "Audira.run JWT"),
    ("Resonode-issued", "Audira.run-issued"),
    ("Resonode logo", "Audira.run logo"),
    ("Resonode Comms Analyzer", "Audira.run Comms Analyzer"),
    ("<ProviderName>Resonode</ProviderName>", "<ProviderName>Audira.run</ProviderName>"),
    ("Map WorkOS directory groups to Resonode roles", "Map WorkOS directory groups to Audira.run roles"),
    ("Where it runs in Resonode", "Where it runs in Audira.run"),
    ("**Product:** Resonode", "**Product:** Audira.run"),
    ("deploying Resonode", "deploying Audira.run"),
    ("exchange for Resonode JWT", "exchange for Audira.run JWT"),
    ("*Resonode*", "*Audira.run*"),
    ("| Product (working) | Resonode", "| Product (working) | Audira.run"),
    ("Resonode — Enterprise Communications", "Audira.run — Enterprise Communications"),
    ("Resonode — Complete", "Audira.run — Complete"),
    ("Resonode — Computed", "Audira.run — Computed"),
    ("Resonode — environment", "Audira.run — environment"),
    ("Resonode — Enterprise", "Audira.run — Enterprise"),
    ("Resonode — pre-send", "Audira.run — pre-send"),
    ("Resonode API — FastAPI", "Audira.run API — FastAPI"),
    ("Resonode design tokens", "Audira.run design tokens"),
    ("Resonode shared core", "Audira.run shared core"),
    ("Resonode session JWT", "Audira.run session JWT"),
    ('iss: str = "resonode"', 'iss: str = "audira"'),
    ('"iss": "resonode"', '"iss": "audira"'),
    ('issuer="resonode"', 'issuer="audira"'),
    ("resonode-api", "audira-api"),
    ("resonode-worker", "audira-worker"),
    ("resonode-db", "audira-db"),
    ("resonode-redis", "audira-redis"),
    ("resonode-artifacts", "audira-artifacts"),
    ("resonode_tribe_", "audira_tribe_"),
    ("resonode_test", "audira_test"),
    ("resonode-admin", "audira-admin"),
    ("resonode-comms", "audira-comms"),
    ("resonode-brand", "audira-brand"),
    ("resonode-security", "audira-security"),
    ("admin@resonode.dev", "admin@audira.run"),
    ("postgresql+asyncpg://resonode:resonode@", "postgresql+asyncpg://audira:audira@"),
    ("POSTGRES_USER: resonode", "POSTGRES_USER: audira"),
    ("POSTGRES_PASSWORD: resonode", "POSTGRES_PASSWORD: audira"),
    ("POSTGRES_DB: resonode", "POSTGRES_DB: audira"),
    ("pg_isready -U resonode", "pg_isready -U audira"),
    ("Resonode API", "Audira.run API"),
    ("# Resonode", "# Audira.run"),
    ("Resonode", "Audira.run"),
]


def should_process(p: Path) -> bool:
    if set(p.parts) & SKIP:
        return False
    if p.suffix in EXT or p.name in ("Dockerfile", "requirements.txt"):
        return True
    return False


def main() -> None:
    count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_process(path):
            continue
        if path.name == "rename_product.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        orig = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            count += 1
            print(path.relative_to(ROOT))
    print(f"Updated {count} files")


if __name__ == "__main__":
    main()
