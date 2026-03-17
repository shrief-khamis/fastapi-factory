"""Load module manifests, check compatibility, and apply module actions to a generated project."""

import sys
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


def append_requirements(project_path: Path, module_names: list[str]) -> None:
    """Append python_packages from each module's manifest to project_path/requirements.txt."""
    requirements_path = project_path / "requirements.txt"
    if not requirements_path.is_file():
        return
    with open(requirements_path) as f:
        content = f.read()
    # Collect already-present package keys so we don't duplicate
    seen = set()
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            seen.add(_pkg_key(line))
    lines_to_append = []
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
    if not lines_to_append:
        return
    suffix = "\n" + "\n".join(lines_to_append)
    if content and not content.endswith("\n"):
        suffix = "\n" + suffix
    with open(requirements_path, "w") as f:
        f.write(content + suffix)


def apply_modules(project_path: Path, template: str, module_names: list[str]) -> None:
    """
    Apply all selected modules to the generated project at project_path.
    Assumes compatibility has already been checked.
    """
    if not module_names:
        return
    append_requirements(project_path, module_names)
    # TODO: copy_files, create_dirs, patches, etc.
    print(f"Applied modules: {', '.join(module_names)}")
