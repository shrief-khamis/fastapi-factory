"""Unit tests for scripts.new_project."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import new_project


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    return tmp_path / "generated"


class TestNewProjectMain:
    def test_generates_template_without_modules(self, out_dir: Path) -> None:
        code = new_project.main(
            [
                "--template",
                "async_io_api",
                "--name",
                "my-api",
                "--path",
                str(out_dir),
            ]
        )
        dest = out_dir / "my-api"
        assert code == 0
        assert dest.is_dir()
        assert (dest / "src" / "main.py").is_file()
        assert (dest / "README.md").is_file()

    def test_generates_template_with_modules(self, out_dir: Path) -> None:
        code = new_project.main(
            [
                "--template",
                "async_io_api",
                "--name",
                "auth-api",
                "--path",
                str(out_dir),
                "--modules",
                "identity_auth",
            ]
        )
        dest = out_dir / "auth-api"
        assert code == 0
        assert (dest / "src" / "db" / "auth.py").is_file()
        assert (dest / "docker-compose.yml").read_text().count("postgres:16") >= 1

    def test_unknown_template_returns_error(self, out_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code = new_project.main(
            [
                "--template",
                "not_a_template",
                "--name",
                "x",
                "--path",
                str(out_dir),
            ]
        )
        assert code == 1
        assert "not found" in capsys.readouterr().err.lower()

    def test_existing_destination_returns_error(
        self, out_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        out_dir.mkdir()
        (out_dir / "my-api").mkdir()
        code = new_project.main(
            [
                "--template",
                "async_io_api",
                "--name",
                "my-api",
                "--path",
                str(out_dir),
            ]
        )
        assert code == 1
        assert "already exists" in capsys.readouterr().err.lower()

    def test_incompatible_modules_return_error(
        self, out_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = new_project.main(
            [
                "--template",
                "async_io_api",
                "--name",
                "bad-api",
                "--path",
                str(out_dir),
                "--modules",
                "webhook_sender",
            ]
        )
        assert code == 1
        assert "not compatible" in capsys.readouterr().err.lower()

    def test_strips_whitespace_in_module_list(self, out_dir: Path) -> None:
        code = new_project.main(
            [
                "--template",
                "celery_job_api",
                "--name",
                "job-api",
                "--path",
                str(out_dir),
                "--modules",
                " webhook_sender ",
            ]
        )
        dest = out_dir / "job-api"
        assert code == 0
        assert (dest / "src" / "api" / "routes" / "webhook_routes.py").is_file()
