from pathlib import Path


def test_project_scaffold_exists() -> None:
    root = Path(__file__).resolve().parents[2]

    expected_paths = [
        root / "PROJECT_SPEC.md",
        root / "services" / "api" / "Dockerfile",
        root / "services" / "model_server" / "Dockerfile",
        root / "services" / "worker" / "Dockerfile",
        root / "docker-compose.yml",
        root / "Makefile",
        root / "docs" / "adr" / "ADR-0001-separate-api-and-model-server.md",
    ]

    for path in expected_paths:
        assert path.exists(), f"Missing scaffold path: {path}"
