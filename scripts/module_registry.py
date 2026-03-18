"""Load module manifests, check compatibility, and apply module actions to a generated project."""

import shutil
from pathlib import Path

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def modules_dir() -> Path:
    return repo_root() / "modules"


def _discover_modules() -> dict[str, tuple[Path, dict]]:
    """Return dict mapping manifest['name'] -> (module_dir, manifest_dict)."""
    result = {}
    base = modules_dir()
    if not base.is_dir():
        return result
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        manifest_path = entry / "manifest.yml"
        if not manifest_path.is_file():
            continue
        with open(manifest_path) as f:
            data = yaml.safe_load(f)
        if data and "name" in data:
            result[data["name"]] = (entry, data)
    return result


def load_manifest(module_name: str) -> tuple[Path, dict] | None:
    """Load manifest for a module by name. Returns (module_dir, manifest) or None if not found."""
    modules = _discover_modules()
    return modules.get(module_name)


def check_compatibility(
    template: str,
    module_names: list[str],
) -> tuple[bool, str]:
    """
    Check that all selected modules are compatible with the template and with each other.
    Returns (ok, error_message). If ok is True, error_message is empty.
    """
    modules = _discover_modules()
    for name in module_names:
        if name not in modules:
            return False, f"Unknown module: {name}"
        _, manifest = modules[name]
        compatible = manifest.get("compatible_templates") or []
        if template not in compatible:
            return False, f"Module '{name}' is not compatible with template '{template}'"
        for req in manifest.get("requires_modules") or []:
            if req not in module_names:
                return False, f"Module '{name}' requires module '{req}'"
        for conflict in manifest.get("conflicts_with") or []:
            if conflict in module_names:
                return False, f"Module '{name}' conflicts with module '{conflict}'"
    return True, ""


def _pkg_key(spec: str) -> str:
    """Normalize a pip spec to a key for deduplication (e.g. 'httpx>=0.27' -> 'httpx')."""
    return spec.split("==")[0].split(">=")[0].split(">")[0].split("[")[0].strip().lower()


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text()


def _append_text(path: Path, text: str) -> None:
    """Append text to the file, ensuring a newline boundary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_text(path)
    if not existing:
        path.write_text(text.lstrip("\n"))
        return
    to_write = existing
    if not to_write.endswith("\n"):
        to_write += "\n"
    to_write += text.lstrip("\n")
    path.write_text(to_write)


def _append_text_if_missing(path: Path, block: str) -> None:
    """Append a block if it isn't already present as a substring."""
    existing = _read_text(path)
    if block.strip() and block.strip() in existing:
        return
    _append_text(path, block)


def _append_lines_unique(path: Path, lines: list[str]) -> None:
    """Append each line if not already present exactly."""
    if not lines:
        return
    existing = _read_text(path)
    existing_lines = set(existing.splitlines())
    to_add = [ln for ln in lines if ln not in existing_lines]
    if not to_add:
        return
    _append_text(path, "\n".join(to_add) + "\n")


def append_requirements(project_path: Path, module_names: list[str]) -> None:
    """Append python_packages from each module's manifest to project_path/requirements.txt."""
    requirements_path = project_path / "requirements.txt"
    if not requirements_path.is_file():
        return
    content = _read_text(requirements_path)
    # Collect already-present package keys so we don't duplicate
    seen = set()
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            seen.add(_pkg_key(line))
    lines_to_append: list[str] = []
    for name in module_names:
        out = load_manifest(name)
        if not out:
            continue
        _, manifest = out
        for pkg in manifest.get("dependencies", {}).get("python_packages") or []:
            key = _pkg_key(pkg)
            if key in seen:
                continue
            seen.add(key)
            lines_to_append.append(pkg)
    _append_lines_unique(requirements_path, lines_to_append)


def append_env_vars(project_path: Path, module_names: list[str]) -> None:
    """Append env vars to .env.example if not present."""
    env_example = project_path / ".env.example"
    existing = _read_text(env_example)
    existing_lines = existing.splitlines()

    def has_var(var_name: str) -> bool:
        prefix = f"{var_name}="
        return any(line.strip().startswith(prefix) for line in existing_lines)

    for name in module_names:
        out = load_manifest(name)
        if not out:
            continue
        _, manifest = out
        env_vars = manifest.get("dependencies", {}).get("env_vars") or []
        to_add = []
        for item in env_vars:
            var_name = item.get("name")
            value = item.get("value", "")
            if not var_name or has_var(var_name):
                continue
            to_add.append(f"{var_name}={value}")
        if not to_add:
            continue
        header = f"# {name} module"
        block_lines = ["", header, *to_add]
        _append_lines_unique(env_example, block_lines)
        existing_lines = _read_text(env_example).splitlines()


def copy_module_files(project_path: Path, module_names: list[str]) -> None:
    """Copy module files into the generated project (skip if destination exists)."""
    for name in module_names:
        out = load_manifest(name)
        if not out:
            continue
        module_dir, manifest = out
        for item in manifest.get("copy_files") or []:
            src_rel = item.get("source")
            dst_rel = item.get("destination")
            if not src_rel or not dst_rel:
                continue
            src = module_dir / src_rel
            dst = project_path / dst_rel
            if dst.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def apply_append_patches(project_path: Path, module_names: list[str]) -> None:
    """Apply append-only patches defined in manifest (content_from or lines)."""
    for name in module_names:
        out = load_manifest(name)
        if not out:
            continue
        module_dir, manifest = out
        for item in manifest.get("append_files") or []:
            target_rel = item.get("target")
            if not target_rel:
                continue
            target = project_path / target_rel
            if "content_from" in item and item["content_from"]:
                patch_path = module_dir / item["content_from"]
                block = _read_text(patch_path)
                _append_text_if_missing(target, block)
            elif "lines" in item and item["lines"]:
                _append_lines_unique(target, list(item["lines"]))


def apply_modules(project_path: Path, template: str, module_names: list[str]) -> None:
    """
    Apply all selected modules to the generated project at project_path.
    Assumes compatibility has already been checked.
    """
    if not module_names:
        return
    copy_module_files(project_path, module_names)
    apply_append_patches(project_path, module_names)
    append_requirements(project_path, module_names)
    append_env_vars(project_path, module_names)
    print(f"Applied modules: {', '.join(module_names)}")
