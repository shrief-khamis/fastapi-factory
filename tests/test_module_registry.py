"""Unit tests for scripts.module_registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import module_registry as registry


class TestPkgKey:
    @pytest.mark.parametrize(
        ("spec", "expected"),
        [
            ("httpx>=0.27.0", "httpx"),
            ("SQLAlchemy==2.0.0", "sqlalchemy"),
            ("uvicorn[standard]>=0.32.0", "uvicorn"),
            ("  FastAPI>=0.115.0  ", "fastapi"),
        ],
    )
    def test_normalizes_package_name(self, spec: str, expected: str) -> None:
        assert registry._pkg_key(spec) == expected


class TestDeepMergeDicts:
    def test_merges_nested_dicts(self) -> None:
        base = {"services": {"api": {"ports": ["8000:8000"]}}}
        overlay = {"services": {"api": {"depends_on": ["db"]}, "db": {"image": "postgres:16"}}}
        merged = registry.deep_merge_dicts(base, overlay)
        assert merged["services"]["api"]["ports"] == ["8000:8000"]
        assert merged["services"]["api"]["depends_on"] == ["db"]
        assert merged["services"]["db"]["image"] == "postgres:16"

    def test_overlay_replaces_scalars_and_lists(self) -> None:
        base = {"count": 1, "tags": ["a"]}
        overlay = {"count": 2, "tags": ["b", "c"]}
        merged = registry.deep_merge_dicts(base, overlay)
        assert merged == {"count": 2, "tags": ["b", "c"]}


class TestInsertTextAfterMarkerLine:
    def test_inserts_block_after_marker(self) -> None:
        content = "line1\n# MARKER\nline3\n"
        block = "inserted\n"
        result = registry.insert_text_after_marker_line(content, "# MARKER", block)
        assert result == "line1\n# MARKER\ninserted\nline3\n"

    def test_returns_none_when_marker_missing(self) -> None:
        assert registry.insert_text_after_marker_line("hello", "# MISSING", "x") is None

    def test_returns_none_for_empty_marker(self) -> None:
        assert registry.insert_text_after_marker_line("hello", "", "x") is None

    def test_idempotent_when_block_already_present(self) -> None:
        content = "before\n# MARKER\nalready there\nafter\n"
        result = registry.insert_text_after_marker_line(content, "# MARKER", "already there")
        assert result == content


class TestResolveModulesForTemplate:
    def test_resolves_requires_modules_in_order(self, fake_modules_dir: Path) -> None:
        resolved, err = registry._resolve_modules_for_template(
            "test_template", ["needs_base"]
        )
        assert err == ""
        assert resolved == ["base_only", "needs_base"]

    def test_resolves_component_dependencies(self, fake_modules_dir: Path) -> None:
        resolved, err = registry._resolve_modules_for_template(
            "test_template", ["bundle_parent"]
        )
        assert err == ""
        assert resolved == ["base_only", "needs_base", "bundle_parent"]

    def test_unknown_module_returns_error(self, fake_modules_dir: Path) -> None:
        resolved, err = registry._resolve_modules_for_template(
            "test_template", ["does_not_exist"]
        )
        assert resolved == []
        assert err == "Unknown module: does_not_exist"

    def test_cyclic_dependency_returns_error(self, fake_modules_dir: Path) -> None:
        resolved, err = registry._resolve_modules_for_template(
            "test_template", ["cycle_a"]
        )
        assert resolved == []
        assert "Cyclic module dependency" in err


class TestCheckCompatibility:
    def test_rejects_incompatible_template(self, fake_modules_dir: Path) -> None:
        ok, err = registry.check_compatibility("test_template", ["wrong_template"])
        assert ok is False
        assert "not compatible with template" in err

    def test_rejects_conflicting_modules(self, fake_modules_dir: Path) -> None:
        ok, err = registry.check_compatibility(
            "test_template", ["conflict_left", "conflict_right"]
        )
        assert ok is False
        assert "conflicts with module" in err

    def test_accepts_valid_module_chain(self, fake_modules_dir: Path) -> None:
        ok, err = registry.check_compatibility("test_template", ["needs_base"])
        assert ok is True
        assert err == ""

    def test_identity_auth_resolves_real_modules(self) -> None:
        ok, err = registry.check_compatibility("async_io_api", ["identity_auth"])
        assert ok is True
        assert err == ""

    def test_webhook_sender_rejects_async_io_api(self) -> None:
        ok, err = registry.check_compatibility("async_io_api", ["webhook_sender"])
        assert ok is False
        assert "not compatible with template" in err


class TestAppendHelpers:
    def test_append_text_if_missing_is_idempotent(self, tmp_path: Path) -> None:
        target = tmp_path / "file.txt"
        target.write_text("existing\n")
        registry._append_text_if_missing(target, "new block\n")
        registry._append_text_if_missing(target, "new block\n")
        assert target.read_text().count("new block") == 1

    def test_append_lines_unique_skips_existing_lines(self, tmp_path: Path) -> None:
        target = tmp_path / "req.txt"
        target.write_text("fastapi>=0.115.0\n")
        registry._append_lines_unique(target, ["fastapi>=0.115.0", "httpx>=0.27.0"])
        lines = target.read_text().splitlines()
        assert lines.count("fastapi>=0.115.0") == 1
        assert "httpx>=0.27.0" in lines


class TestAppendRequirements:
    def test_deduplicates_existing_packages(self, project_dir: Path, fake_modules_dir: Path) -> None:
        registry.append_requirements(project_dir, ["patch_module"])
        first = project_dir / "requirements.txt"
        registry.append_requirements(project_dir, ["patch_module"])
        text = first.read_text()
        assert text.lower().count("httpx") == 1
        assert "sqlalchemy>=2.0.0" in text.lower()


class TestAppendEnvVars:
    def test_appends_module_env_block_once(self, project_dir: Path, fake_modules_dir: Path) -> None:
        registry.append_env_vars(project_dir, ["patch_module"])
        registry.append_env_vars(project_dir, ["patch_module"])
        text = (project_dir / ".env.example").read_text()
        assert text.count("PATCH_MODULE_VAR=patch-value") == 1
        assert "# patch_module module" in text


class TestCreateDirs:
    def test_creates_declared_directories(self, project_dir: Path, fake_modules_dir: Path) -> None:
        registry.create_dirs(project_dir, ["patch_module"])
        assert (project_dir / "src" / "extra").is_dir()


class TestCopyModuleFiles:
    def test_copies_new_files_and_respects_overwrite(
        self, project_dir: Path, fake_modules_dir: Path
    ) -> None:
        (project_dir / "existing.txt").write_text("keep me\n")
        (project_dir / "overwrite.txt").write_text("old\n")
        registry.copy_module_files(project_dir, ["patch_module"])
        assert (project_dir / "copied.txt").read_text() == "patched route\n"
        assert (project_dir / "existing.txt").read_text() == "keep me\n"
        assert (project_dir / "overwrite.txt").read_text() == "new overwrite content\n"


class TestApplyPatches:
    def test_file_append_marker_insert_and_yml_merge(
        self, project_dir: Path, fake_modules_dir: Path
    ) -> None:
        registry.apply_patches(project_dir, ["patch_module"])

        routes = (project_dir / "src" / "api" / "routes" / "__init__.py").read_text()
        assert "appended router" in routes

        dockerfile = (project_dir / "Dockerfile").read_text()
        assert "COPY alembic/" in dockerfile

        compose = (project_dir / "docker-compose.yml").read_text()
        assert "postgres:16" in compose
        assert "depends_on" in compose
        assert "postgres_data" in compose

    def test_file_append_is_idempotent(self, project_dir: Path, fake_modules_dir: Path) -> None:
        registry.apply_patches(project_dir, ["patch_module"])
        routes_after_first = (
            project_dir / "src" / "api" / "routes" / "__init__.py"
        ).read_text()
        registry.apply_patches(project_dir, ["patch_module"])
        routes_after_second = (
            project_dir / "src" / "api" / "routes" / "__init__.py"
        ).read_text()
        assert routes_after_second == routes_after_first


class TestApplyModules:
    def test_raises_on_unresolved_dependency(self, project_dir: Path, fake_modules_dir: Path) -> None:
        with pytest.raises(ValueError, match="Unknown module"):
            registry.apply_modules(project_dir, "test_template", ["does_not_exist"])

    def test_no_op_for_empty_module_list(self, project_dir: Path) -> None:
        before = (project_dir / "requirements.txt").read_text()
        registry.apply_modules(project_dir, "test_template", [])
        assert (project_dir / "requirements.txt").read_text() == before

    def test_applies_patch_module_end_to_end(
        self, project_dir: Path, fake_modules_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        registry.apply_modules(project_dir, "test_template", ["patch_module"])
        captured = capsys.readouterr()
        assert "Applied modules: patch_module" in captured.out
        assert (project_dir / "copied.txt").exists()
        assert "PATCH_MODULE_VAR=patch-value" in (project_dir / ".env.example").read_text()
