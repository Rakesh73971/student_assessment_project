from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"


def test_root_ci_workflow_exists_and_checks_backend_frontend_docker():
    workflow_path = ROOT / ".github" / "workflows" / "ci.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    assert workflow["name"] == "CI"
    assert {"backend", "frontend", "docker"}.issubset(workflow["jobs"])


def test_dockerfile_uses_python_module_uvicorn():
    dockerfile = (BACKEND / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert 'CMD ["python", "-m", "uvicorn"' in dockerfile


def test_compose_has_database_healthcheck_and_backend_db_hostname():
    compose = yaml.safe_load((BACKEND / "docker-compose.yml").read_text(encoding="utf-8"))

    assert "healthcheck" in compose["services"]["db"]
    assert compose["services"]["backend"]["environment"]["DATABASE_HOSTNAME"] == "db"
    assert compose["services"]["backend"]["depends_on"]["db"]["condition"] == "service_healthy"
