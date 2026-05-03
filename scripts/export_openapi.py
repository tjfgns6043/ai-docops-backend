"""Export OpenAPI schema."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    """Export OpenAPI schema."""
    from services.api.app.main import create_app

    path = Path("docs/openapi.json")
    path.write_text(json.dumps(create_app().openapi(), indent=2), encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
