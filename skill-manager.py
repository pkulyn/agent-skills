#!/usr/bin/env python3
"""Agent Skills Manager - Claude Code Agent Skill管理工具

用法:
    python skill-manager.py list                 列出所有skill
    python skill-manager.py status [SKILL_ID]    查看skill详细状态
    python skill-manager.py sync                 扫描磁盘，更新skills.json
    python skill-manager.py pull [SKILL_ID]      批量/单个git pull
    python skill-manager.py diff [SKILL_ID]      查看远程未拉取的commit
    python skill-manager.py init <ID> --name --category  创建新skill
    python skill-manager.py validate [--fix]     校验frontmatter + 密钥扫描
    python skill-manager.py doctor               一键巡检
    python skill-manager.py archive <ID>         归档废弃skill
    python skill-manager.py install <ID...>      从远程仓库安装skill
    python skill-manager.py install --list       列出远程可用skill
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT_DIR = Path(__file__).parent.resolve()
SKILLS_DIR = ROOT_DIR / "skills"
MANIFEST_PATH = ROOT_DIR / "skills.json"
ARCHIVE_DIR = ROOT_DIR / "archive"
DEFAULT_REMOTE = "pkulyn/agent-skills"
TEMPLATE_PATH = ROOT_DIR / "templates" / "SKILL.md.template"

VALID_CATEGORIES = [
    "media-processing",
    "agent-tooling",
    "writing",
    "knowledge-management",
    "data-processing",
    "document-generation",
    "productivity",
    "dev-tools",
]

VALID_TYPES = ["tool-wrapper", "code-generator", "prompt-skill"]

SECRET_PATTERNS = [
    re.compile(r'(?:sk-|sk_live_|sk_test_)[a-zA-Z0-9]{20,}', re.IGNORECASE),
    re.compile(r'(?:AKIA|ASIA)[0-9A-Z]{16}'),
    re.compile(r'(?:ghp|gho|ghu|ghs|ghc)_[a-zA-Z0-9]{36,}'),
    re.compile(r'(?:Bearer\s+)[a-zA-Z0-9\-._~+/]+=*'),
    re.compile(r'(?:api[_-]?key\s*[:=]\s*["\']?)[a-zA-Z0-9]{20,}', re.IGNORECASE),
    re.compile(r'(?:secret[_-]?key\s*[:=]\s*["\']?)[a-zA-Z0-9]{20,}', re.IGNORECASE),
]


# ── Manifest I/O ──────────────────────────────────────────────

def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": 1, "updated": None, "skills": {}}


def save_manifest(data):
    data["updated"] = datetime.now().isoformat()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Manifest saved to {MANIFEST_PATH}")


# ── SKILL.md parsing ─────────────────────────────────────────

def parse_frontmatter(skill_md_path):
    """Parse YAML frontmatter from SKILL.md.

    Uses PyYAML when available for robust handling of all YAML features.
    Falls back to a simple hand-rolled parser for basic cases.
    Handles both new format (metadata: block) and legacy top-level fields.
    """
    text = skill_md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    end = text.find("---", 3)
    if end == -1:
        return None, text
    fm_text = text[3:end].strip()
    body = text[end + 3:]

    fm = None
    if HAS_YAML:
        try:
            fm = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError:
            fm = None

    if fm is None:
        # Fallback: minimal parser for basic key: value
        fm = {}
        for line in fm_text.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith(" "):
                continue
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val and val not in ("|", ">"):
                    fm[key] = val

    if not isinstance(fm, dict):
        fm = {}

    # Ensure metadata dict exists
    if "metadata" not in fm or not isinstance(fm.get("metadata"), dict):
        fm["metadata"] = {}

    # Migrate legacy top-level fields into metadata for unified access
    meta = fm["metadata"]
    for field in ("version", "category", "type", "author", "tags"):
        if field in fm and field not in meta:
            meta[field] = fm[field]

    return fm, body


def parse_frontmatter_from_text(text):
    """Parse YAML frontmatter from raw text string (not a file path)."""
    if not text.startswith("---"):
        return None, text
    end = text.find("---", 3)
    if end == -1:
        return None, text
    fm_text = text[3:end].strip()
    body = text[end + 3:]

    fm = None
    if HAS_YAML:
        try:
            fm = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError:
            fm = None

    if fm is None:
        fm = {}
        for line in fm_text.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith(" "):
                continue
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val and val not in ("|", ">"):
                    fm[key] = val

    if not isinstance(fm, dict):
        fm = {}

    if "metadata" not in fm or not isinstance(fm.get("metadata"), dict):
        fm["metadata"] = {}

    meta = fm["metadata"]
    for field in ("version", "category", "type", "author", "tags"):
        if field in fm and field not in meta:
            meta[field] = fm[field]

    return fm, body
    """Normalize version to semver (MAJOR.MINOR.PATCH)."""
    if v is None:
        return "0.1.0"
    v = str(v).strip().strip('"').strip("'")
    if not v:
        return "0.1.0"
    parts = v.split(".")
    while len(parts) < 3:
        parts.append("0")
    return ".".join(parts[:3])


# ── Git helpers ───────────────────────────────────────────────

def git_run(dir_path, *args):
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=str(dir_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result
    except FileNotFoundError:
        return None


def git_status(dir_path):
    """Return git status info for a directory."""
    info = {"enabled": False, "remote": None, "branch": None, "has_uncommitted": None, "ahead": 0, "behind": 0}
    git_dir = dir_path / ".git"
    if not git_dir.exists():
        return info
    info["enabled"] = True

    r = git_run(dir_path, "remote", "get-url", "origin")
    if r and r.returncode == 0:
        info["remote"] = r.stdout.strip()

    r = git_run(dir_path, "rev-parse", "--abbrev-ref", "HEAD")
    if r and r.returncode == 0:
        info["branch"] = r.stdout.strip()

    r = git_run(dir_path, "status", "--porcelain")
    if r and r.returncode == 0:
        info["has_uncommitted"] = bool(r.stdout.strip())

    r = git_run(dir_path, "log", "--format=%ci", "-1")
    if r and r.returncode == 0 and r.stdout.strip():
        try:
            dt = datetime.fromisoformat(r.stdout.strip().rsplit("+", 1)[0].strip())
            info["last_commit_date"] = dt.strftime("%Y-%m-%d")
        except (ValueError, IndexError):
            info["last_commit_date"] = None
    else:
        info["last_commit_date"] = None

    return info


def git_pull(dir_path):
    r = git_run(dir_path, "pull", "--ff-only")
    if r is None:
        return "ERROR: git not found"
    if r.returncode == 0:
        if "Already up to date" in r.stdout or "Already up-to-date" in r.stdout:
            return "already up-to-date"
        return "updated"
    return f"FAILED: {r.stderr.strip()[:80]}"


def git_fetch_diff(dir_path):
    """Fetch and show commits on remote not in local."""
    r = git_run(dir_path, "fetch")
    if r is None or r.returncode != 0:
        return None
    r = git_run(dir_path, "log", "HEAD..@{upstream}", "--oneline")
    if r is None:
        return None
    if r.returncode != 0:
        r2 = git_run(dir_path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
        upstream = r2.stdout.strip() if r2 and r2.returncode == 0 else "origin/HEAD"
        r = git_run(dir_path, "log", f"HEAD..{upstream}", "--oneline")
        if r is None or r.returncode != 0:
            return None
    return r.stdout.strip()


# ── Secret scanning ───────────────────────────────────────────

def scan_secrets(dir_path):
    """Scan all text files in a skill directory for hardcoded secrets."""
    findings = []
    for root, _dirs, files in os.walk(dir_path):
        # Skip .git directories
        if ".git" in root.split(os.sep):
            continue
        for fname in files:
            fpath = Path(root) / fname
            # Skip binary files
            try:
                text = fpath.read_text(encoding="utf-8", errors="strict")
            except (UnicodeDecodeError, PermissionError):
                continue
            for pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    rel = fpath.relative_to(dir_path)
                    line_num = text[: match.start()].count("\n") + 1
                    findings.append(f"{rel}:{line_num} - possible secret ({match.group()[:20]}...)")
    return findings


# ── Discover skills on disk ──────────────────────────────────

def discover_skills():
    """Scan skills/ directory for all subdirs containing SKILL.md."""
    skills = {}
    if not SKILLS_DIR.exists():
        return skills
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name == "__pycache__":
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue

        fm, _ = parse_frontmatter(skill_md)
        name = fm.get("name", entry.name) if fm else entry.name
        metadata = fm.get("metadata", {}) if fm else {}
        desc = fm.get("description", "") if fm else ""
        license_val = fm.get("license", "") if fm else ""

        # Count files in skill directory
        file_count = sum(1 for _ in entry.rglob("*") if _.is_file() and ".git" not in _.parts)

        skill_data = {
            "name": name,
            "description": desc[:120] + ("..." if len(desc) > 120 else ""),
            "directory": entry.name,
            "license": license_val or None,
            "metadata": {
                "version": normalize_version(metadata.get("version")),
                "category": metadata.get("category", ""),
                "type": metadata.get("type", ""),
                "author": metadata.get("author", ""),
                "tags": metadata.get("tags", []),
            },
            "files": file_count,
        }

        skills[name] = skill_data
    return skills


# ── CLI Commands ──────────────────────────────────────────────

def cmd_list(args):
    """List all skills in a table."""
    manifest = load_manifest()
    skills = manifest.get("skills", {})
    if not skills:
        print("No skills found. Run 'sync' first.")
        return

    if args.json:
        print(json.dumps(skills, ensure_ascii=False, indent=2))
        return

    # Table header
    print(f"{'NAME':<24} {'VERSION':<10} {'CATEGORY':<22} {'TYPE':<16} {'FILES':<6}")
    print("-" * 78)
    for _sid, s in sorted(skills.items()):
        meta = s.get("metadata", {})
        version = meta.get("version", "?")
        category = meta.get("category", "-")
        skill_type = meta.get("type", "-")
        files = s.get("files", "?")
        print(f"{s.get('name', '?'):<24} {version:<10} {category:<22} {skill_type:<16} {files:<6}")


def cmd_status(args):
    """Show detailed status for one or all skills."""
    manifest = load_manifest()
    skills = manifest.get("skills", {})

    if args.skill_id:
        targets = {args.skill_id: skills.get(args.skill_id)}
        if not targets[args.skill_id]:
            print(f"Skill '{args.skill_id}' not found in manifest.")
            return
    else:
        targets = skills

    for sid, s in sorted(targets.items()):
        meta = s.get("metadata", {})
        dir_name = s.get("directory", sid)

        print(f"\n{'=' * 50}")
        print(f"  {s.get('name', sid)} v{meta.get('version', '?')}")
        print(f"{'=' * 50}")
        print(f"  Directory:  skills/{dir_name}")
        print(f"  Category:   {meta.get('category', '-')}")
        print(f"  Type:       {meta.get('type', '-')}")
        print(f"  Author:     {meta.get('author', '-')}")
        print(f"  License:    {s.get('license', '-') or '-'}")
        print(f"  Files:      {s.get('files', '?')}")
        print(f"  Description: {s.get('description', '-')[:100]}")


def cmd_sync(args):
    """Scan disk and update skills.json."""
    skills = discover_skills()
    manifest = load_manifest()
    manifest["skills"] = skills
    save_manifest(manifest)

    print(f"\n{'=' * 50}")
    print(f"Found {len(skills)} skill(s):")
    for sid, s in sorted(skills.items()):
        meta = s.get("metadata", {})
        print(f"  + {sid} (v{meta.get('version', '?')}, {meta.get('category', '-')}, {meta.get('type', '-')})")


def cmd_pull(args):
    """Git pull from the root monorepo."""
    result = git_pull(ROOT_DIR)
    print(f"monorepo: {result}")
    if result == "updated":
        # Re-sync after pull
        cmd_sync(args)


def cmd_diff(args):
    """Show remote commits not yet pulled."""
    result = git_fetch_diff(ROOT_DIR)
    if result is None:
        print("Could not fetch from remote. Is a remote configured?")
    elif result:
        print("Remote has updates:")
        print(result)
    else:
        print("Up-to-date.")


def cmd_init(args):
    """Create a new skill from template."""
    skill_id = args.skill_id
    if not re.match(r'^[a-z][a-z0-9-]*$', skill_id):
        print(f"ERROR: skill_id must be kebab-case (lowercase, digits, hyphens), got: {skill_id}")
        return 1

    skill_dir = SKILLS_DIR / skill_id
    if skill_dir.exists():
        print(f"ERROR: directory already exists: {skill_dir}")
        return 1

    display_name = args.name or skill_id.replace("-", " ").title()
    category = args.category or "productivity"
    description = args.description or f"{display_name} skill"
    skill_type = args.type or "prompt-skill"

    # Read template
    template_text = ""
    if TEMPLATE_PATH.exists():
        template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
        template_text = template_text.replace("{{SKILL_ID}}", skill_id)
        template_text = template_text.replace("{{DISPLAY_NAME}}", display_name)
        template_text = template_text.replace("{{DESCRIPTION}}", description)
        template_text = template_text.replace("{{CATEGORY}}", category)
        template_text = template_text.replace("{{TYPE}}", skill_type)
        template_text = template_text.replace("{{TAGS}}", category)
    else:
        template_text = f"""---
name: {skill_id}
description: |
  {description}
license: MIT
metadata:
  version: "0.1.0"
  category: {category}
  type: {skill_type}
  author: pkulyn
  tags: [{category}]
model: inherit
---

# {display_name}

## Overview

{description}

## Usage

TBD

## Configuration

TBD
"""

    # Create directory structure
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(template_text, encoding="utf-8")
    (skill_dir / "README.md").write_text(f"# {display_name}\n\n{description}\n", encoding="utf-8")
    (skill_dir / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n.env\n.venv/\n.vscode/\n.idea/\nThumbs.db\n.DS_Store\nnode_modules/\n",
        encoding="utf-8",
    )
    (skill_dir / "LICENSE").write_text(
        "MIT License\n\nCopyright (c) " + str(datetime.now().year) + " pkulyn\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy "
        "of this software and associated documentation files (the \"Software\"), to deal "
        "in the Software without restriction, including without limitation the rights "
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
        "copies of the Software, and to permit persons to whom the Software is "
        "furnished to do so, subject to the following conditions:\n\n"
        "The above copyright notice and this permission notice shall be included in all "
        "copies or substantial portions of the Software.\n\n"
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
        "SOFTWARE.\n",
        encoding="utf-8",
    )

    print(f"Created {skill_dir}/")
    print(f"  SKILL.md (from template)")
    print(f"  README.md")
    print(f"  .gitignore")
    print(f"  LICENSE (MIT)")

    # In monorepo mode, no separate git init needed
    # Sync manifest
    manifest = load_manifest()
    skills = discover_skills()
    manifest["skills"] = skills
    save_manifest(manifest)

    return 0


def cmd_validate(args):
    """Validate SKILL.md frontmatter and scan for secrets."""
    manifest = load_manifest()
    skills = manifest.get("skills", {})

    if not skills:
        print("No skills in manifest. Run 'sync' first.")
        return

    total_errors = 0
    total_warnings = 0
    fixes_applied = []

    for sid, s in sorted(skills.items()):
        dir_name = s.get("directory", sid)
        dir_path = SKILLS_DIR / dir_name
        skill_md = dir_path / "SKILL.md"

        errors = []
        warnings = []

        # Check SKILL.md exists
        if not skill_md.exists():
            errors.append("SKILL.md not found")
            total_errors += 1
            print(f"\n{sid}: ERRORS")
            for e in errors:
                print(f"  ✗ {e}")
            continue

        # Parse frontmatter
        fm, body = parse_frontmatter(skill_md)

        # Required fields
        if not fm.get("name"):
            errors.append("missing required field 'name'")
        elif fm["name"] != dir_name and fm["name"] != dir_name.lower():
            warnings.append(f"name '{fm['name']}' does not match directory '{dir_name}'")

        if not fm.get("description"):
            errors.append("missing required field 'description'")

        # Metadata block
        metadata = fm.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        if not metadata.get("version"):
            warnings.append("missing 'metadata.version'")
        else:
            v = str(metadata["version"])
            if len(v.split(".")) < 3:
                warnings.append(f"version '{v}' should be semver 3-part (e.g. '{normalize_version(v)}')")

        if not metadata.get("category"):
            warnings.append("missing 'metadata.category'")
        elif metadata["category"] not in VALID_CATEGORIES:
            warnings.append(f"category '{metadata['category']}' not in valid set: {', '.join(VALID_CATEGORIES)}")

        if not metadata.get("type"):
            warnings.append("missing 'metadata.type'")
        elif metadata["type"] not in VALID_TYPES:
            warnings.append(f"type '{metadata['type']}' not in valid set: {', '.join(VALID_TYPES)}")

        if not fm.get("license"):
            warnings.append("missing 'license'")

        if not metadata.get("author"):
            warnings.append("missing 'metadata.author'")

        # Secret scanning
        secret_findings = scan_secrets(dir_path)
        for finding in secret_findings:
            errors.append(f"possible secret: {finding}")

        total_errors += len(errors)
        total_warnings += len(warnings)

        # Print results
        status = "OK" if not errors and not warnings else ("ERRORS" if errors else "WARNINGS")
        print(f"\n{sid}: {status}")
        for e in errors:
            print(f"  [X] {e}")
        for w in warnings:
            print(f"  [!] {w}")

        # Auto-fix
        if args.fix and (errors or warnings):
            fixes = fix_frontmatter(skill_md, fm, dir_name, sid)
            if fixes:
                fixes_applied.extend([f"{sid}: {f}" for f in fixes])

    if fixes_applied:
        print(f"\n{'=' * 50}")
        print("Fixes applied:")
        for f in fixes_applied:
            print(f"  [+] {f}")

    print(f"\n{'=' * 50}")
    print(f"Summary: {len(skills)} skills, {total_errors} errors, {total_warnings} warnings")

    return 1 if total_errors > 0 else 0


def fix_frontmatter(skill_md_path, fm, dir_name, sid):
    """Auto-fix frontmatter issues using PyYAML. Returns list of fix descriptions."""
    fixes = []
    text = skill_md_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return fixes

    end = text.find("---", 3)
    if end == -1:
        return fixes

    body = text[end + 3:]

    # Work on a copy of the parsed frontmatter
    new_fm = dict(fm)
    metadata = dict(new_fm.get("metadata", {}))
    if not isinstance(metadata, dict):
        metadata = {}

    # Fix name
    if not new_fm.get("name") or new_fm["name"] != dir_name:
        new_fm["name"] = dir_name
        fixes.append(f"name set to '{dir_name}'")

    # Remove top-level legacy fields that belong in metadata
    for field in ("version", "category", "type", "author", "tags"):
        if field in new_fm:
            if field not in metadata:
                metadata[field] = new_fm[field]
            del new_fm[field]

    # Fix version
    if not metadata.get("version"):
        metadata["version"] = "0.1.0"
        fixes.append("version set to '0.1.0'")
    else:
        v = str(metadata["version"])
        normalized = normalize_version(v)
        if v != normalized:
            metadata["version"] = normalized
            fixes.append(f"version normalized '{v}' -> '{normalized}'")

    # Fix category
    if not metadata.get("category"):
        metadata["category"] = "productivity"
        fixes.append("category set to 'productivity'")

    # Fix type
    current_type = metadata.get("type", "")
    if current_type and current_type not in VALID_TYPES:
        metadata["type"] = "prompt-skill"
        fixes.append(f"type '{current_type}' -> 'prompt-skill' (moved to metadata)")
    elif not current_type:
        metadata["type"] = "prompt-skill"
        fixes.append("type set to 'prompt-skill'")

    # Fix author
    if not metadata.get("author"):
        metadata["author"] = "pkulyn"
        fixes.append("author set to 'pkulyn'")

    # Fix license
    if not new_fm.get("license"):
        new_fm["license"] = "MIT"
        fixes.append("license added: MIT")

    new_fm["metadata"] = metadata

    # Reconstruct file using PyYAML
    if HAS_YAML:
        fm_text = yaml.dump(new_fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    else:
        # Fallback: basic serialization
        lines = []
        for k, v in new_fm.items():
            if k == "metadata":
                lines.append("metadata:")
                for mk, mv in v.items():
                    lines.append(f"  {mk}: {mv}")
            elif isinstance(v, str) and "\n" in v:
                lines.append(f"{k}: |")
                for vl in v.split("\n"):
                    lines.append(f"  {vl}")
            else:
                lines.append(f"{k}: {v}")
        fm_text = "\n".join(lines)

    new_text = f"---\n{fm_text}\n---{body}"
    skill_md_path.write_text(new_text, encoding="utf-8")

    return fixes


def cmd_doctor(args):
    """Run sync + validate + git status check."""
    print("Running doctor...\n")
    print("-- Sync --")
    cmd_sync(args)
    print("\n-- Validate --")
    validate_args = argparse.Namespace(fix=args.fix, skill_id=None, json=False)
    result = cmd_validate(validate_args)
    print("\n-- Git Status (root repo) --")
    git_info = git_status(ROOT_DIR)
    if git_info.get("enabled"):
        status = "dirty" if git_info.get("has_uncommitted") else "clean"
        print(f"  Branch: {git_info.get('branch', '?')}")
        print(f"  Status: {status}")
        print(f"  Remote: {git_info.get('remote', 'none')}")
    else:
        print("  Root repo not a git repository")
    print("\nDoctor complete.")


def cmd_archive(args):
    """Move a skill to archive/."""
    sid = args.skill_id
    manifest = load_manifest()
    skills = manifest.get("skills", {})

    if sid not in skills:
        print(f"Skill '{sid}' not found in manifest.")
        return 1

    dir_name = skills[sid].get("directory", sid)
    src = SKILLS_DIR / dir_name
    if not src.exists():
        print(f"Directory not found: {src}")
        return 1

    ARCHIVE_DIR.mkdir(exist_ok=True)
    dest = ARCHIVE_DIR / dir_name
    if dest.exists():
        print(f"Archive target already exists: {dest}")
        return 1

    import shutil
    shutil.move(str(src), str(dest))
    del skills[sid]
    save_manifest(manifest)
    print(f"Archived '{sid}' -> archive/{dir_name}/")
    return 0


# ── Install from remote ────────────────────────────────────────

def _api_request(url, token=None):
    """Make a GitHub API request and return parsed JSON."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "skill-manager"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return None
            return json.loads(body)
    except HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        if e.code == 403 and "rate limit" in err_body.lower():
            print("ERROR: GitHub API rate limit exceeded. Set --token or use 'gh auth token'.")
        elif e.code == 404:
            print(f"ERROR: Not found (404): {url}")
        else:
            print(f"ERROR: HTTP {e.code} for {url}: {err_body[:80]}")
        return None
    except URLError as e:
        print(f"ERROR: Network error: {e.reason}")
        return None


def _get_gh_token():
    """Try to get a GitHub token from gh CLI."""
    try:
        r = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except FileNotFoundError:
        pass
    # Also try the portable gh path
    try:
        gh_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "gh", "gh.exe")
        if os.path.exists(gh_path):
            r = subprocess.run(
                [gh_path, "auth", "token"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
    except Exception:
        pass
    return None


def _download_repo_zip(repo):
    """Download the repo as a zip archive.

    Strategy order:
    1. GitHub API (zipball endpoint)
    2. git archive (remote)
    3. Shallow clone + local zip
    """
    token = _get_gh_token()

    # 1. Try GitHub API zipball
    url = f"https://api.github.com/repos/{repo}/zipball/master"
    headers = {"User-Agent": "skill-manager", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
            if len(data) > 100:
                return BytesIO(data)
    except (HTTPError, URLError, OSError):
        pass

    # 2. Try git archive
    try:
        result = subprocess.run(
            ["git", "archive", "--format=zip", f"--remote=https://github.com/{repo}.git", "HEAD"],
            capture_output=True, timeout=60,
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            return BytesIO(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 3. Shallow clone + zip
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="skill-mgr-")
    try:
        r = subprocess.run(
            ["git", "clone", "--depth=1", f"https://github.com/{repo}.git", tmp_dir],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
        if r.returncode == 0:
            buf = BytesIO()
            import zipfile as zf_mod
            skills_src = Path(tmp_dir) / "skills"
            if skills_src.exists():
                with zf_mod.ZipFile(buf, "w", zf_mod.ZIP_DEFLATED) as zf:
                    for fpath in skills_src.rglob("*"):
                        if fpath.is_file() and ".git" not in fpath.parts:
                            arcname = str(fpath.relative_to(tmp_dir))
                            zf.write(fpath, arcname)
                buf.seek(0)
                return buf
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    finally:
        import shutil
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

    print("ERROR: Could not download repo (API, git archive, and clone all failed)")
    print("  - If behind a corporate proxy, try: python skill-manager.py install <id> --source /path/to/local/repo")
    return None


def _extract_skill_from_zip(zip_bytes, skill_id, dest_dir):
    """Extract a specific skill directory from the repo zip."""
    with zipfile.ZipFile(zip_bytes) as zf:
        names = zf.namelist()

        # Determine path prefix: GitHub format has "owner-repo-hash/" prefix, our format has "skills/"
        skill_prefix = None
        for name in names:
            # GitHub archive format: "pkulyn-agent-skills-abc1234/skills/skill-id/..."
            if f"/skills/{skill_id}/" in name:
                idx = name.index(f"/skills/{skill_id}/")
                skill_prefix = name[:idx + len(f"/skills/{skill_id}/")]
                break
            # Our shallow-clone format: "skills/skill-id/..."
            if name.startswith(f"skills/{skill_id}/"):
                skill_prefix = f"skills/{skill_id}/"
                break

        if skill_prefix is None:
            return False

        extracted = 0
        for name in names:
            if name.startswith(skill_prefix) and not name.endswith("/"):
                under_skill = name[len(skill_prefix):]
                if not under_skill:
                    continue
                target_path = dest_dir / under_skill
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as src, open(target_path, "wb") as dst:
                    dst.write(src.read())
                extracted += 1
        return extracted > 0


def _install_from_local(source_path, skill_ids, dest_dir, force=False):
    """Install skills from a local repo or directory."""
    source = Path(source_path).resolve()
    skills_src = source / "skills" if (source / "skills").exists() else source

    if not skills_src.exists():
        print(f"ERROR: Source directory not found: {source}")
        return 1

    installed = []
    skipped = []

    for sid in skill_ids:
        src_skill = skills_src / sid
        target = dest_dir / sid

        if not src_skill.exists() or not (src_skill / "SKILL.md").exists():
            print(f"  [NOT FOUND] {sid} (no skills/{sid}/SKILL.md in source)")
            skipped.append(sid)
            continue

        if target.exists() and not force:
            print(f"  [SKIP] {sid} (already exists, use --force to overwrite)")
            skipped.append(sid)
            continue

        import shutil
        if target.exists() and force:
            shutil.rmtree(target)

        shutil.copytree(str(src_skill), str(target), ignore=shutil.ignore_patterns(".git"))
        installed.append(sid)
        print(f"  [OK] {sid}")

    return installed, skipped


def cmd_install(args):
    """Install one or more skills from a remote repository or local source."""
    repo = args.repo or DEFAULT_REMOTE
    skill_ids = args.skill_ids
    dest = Path(args.dest) if args.dest else SKILLS_DIR
    token = args.token or _get_gh_token()

    # --list: list available skills
    if args.list_remote:
        source = args.source
        if source:
            # List from local source
            src_path = Path(source).resolve()
            skills_src = src_path / "skills" if (src_path / "skills").exists() else src_path
            if not skills_src.exists():
                print(f"ERROR: Source directory not found: {source}")
                return 1
            print(f"\nAvailable skills in {source}:")
            print(f"{'NAME':<28} {'DESCRIPTION'}")
            print("-" * 60)
            for entry in sorted(skills_src.iterdir()):
                if entry.is_dir() and (entry / "SKILL.md").exists():
                    fm, _ = parse_frontmatter(entry / "SKILL.md")
                    desc = fm.get("description", "")[:50] if fm else ""
                    print(f"  {entry.name:<26} {desc}")
            return 0

        # List from remote
        print(f"Fetching available skills from {repo}...")
        zip_bytes = _download_repo_zip(repo)
        if zip_bytes is None:
            print("  Tip: Use --source /path/to/local/repo to list from a local clone")
            return 1

        with zipfile.ZipFile(zip_bytes) as zf:
            names = zf.namelist()
            skill_dirs = set()
            for name in names:
                for pattern in ["skills/", "/skills/"]:
                    idx = name.find(pattern)
                    if idx >= 0:
                        rest = name[idx + len(pattern):]
                        slash = rest.find("/")
                        if slash > 0:
                            skill_dirs.add(rest[:slash])

        if not skill_dirs:
            print("No skills found in remote repository.")
            return 1

        print(f"\nAvailable skills in {repo}:")
        print(f"{'NAME':<28} {'DESCRIPTION'}")
        print("-" * 60)
        for name in sorted(skill_dirs):
            print(f"  {name}")
        return 0

    if not skill_ids:
        print("ERROR: Specify skill IDs to install, or use --list to see available skills.")
        return 1

    dest.mkdir(parents=True, exist_ok=True)

    # Install from local source
    if args.source:
        print(f"Installing from local source: {args.source}")
        installed, skipped = _install_from_local(args.source, skill_ids, dest, force=args.force)
    else:
        # Install from remote
        print(f"Downloading {repo}...")
        zip_bytes = _download_repo_zip(repo)
        if zip_bytes is None:
            print("  Tip: Use --source /path/to/local/repo to install from a local clone")
            return 1

        installed = []
        skipped = []

        for sid in skill_ids:
            target = dest / sid
            if target.exists() and not args.force:
                print(f"  [SKIP] {sid} (already exists, use --force to overwrite)")
                skipped.append(sid)
                continue

            if target.exists() and args.force:
                import shutil
                shutil.rmtree(target)

            print(f"  Installing {sid}...", end=" ")
            if _extract_skill_from_zip(zip_bytes, sid, target):
                installed.append(sid)
                print("[OK]")
            else:
                print("[NOT FOUND]")
                if target.exists() and not any(target.iterdir()):
                    target.rmdir()
                skipped.append(sid)

    if installed:
        print(f"\nInstalled {len(installed)} skill(s): {', '.join(installed)}")
        print(f"  Destination: {dest}")
        # Sync if installing into local skills dir
        if dest.resolve() == SKILLS_DIR.resolve():
            manifest = load_manifest()
            skills = discover_skills()
            manifest["skills"] = skills
            save_manifest(manifest)

    if skipped:
        print(f"Skipped: {', '.join(skipped)}")

    return 0 if installed else 1


# ── Main ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agent Skills Manager - Claude Code Agent Skill管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    p_list = subparsers.add_parser("list", help="列出所有skill")
    p_list.add_argument("--json", action="store_true", help="JSON格式输出")

    # status
    p_status = subparsers.add_parser("status", help="查看skill详细状态")
    p_status.add_argument("skill_id", nargs="?", help="Skill ID (留空则显示全部)")

    # sync
    subparsers.add_parser("sync", help="扫描磁盘，更新skills.json")

    # pull
    p_pull = subparsers.add_parser("pull", help="批量/单个git pull")
    p_pull.add_argument("skill_id", nargs="?", help="Skill ID (留空则拉取全部)")

    # diff
    p_diff = subparsers.add_parser("diff", help="查看远程未拉取的commit")
    p_diff.add_argument("skill_id", nargs="?", help="Skill ID (留空则检查全部)")

    # init
    p_init = subparsers.add_parser("init", help="创建新skill")
    p_init.add_argument("skill_id", help="Skill ID (kebab-case)")
    p_init.add_argument("--name", help="显示名称")
    p_init.add_argument("--category", help="分类", default="productivity")
    p_init.add_argument("--type", help="类型", default="prompt-skill", choices=VALID_TYPES)
    p_init.add_argument("--description", help="描述")

    # validate
    p_validate = subparsers.add_parser("validate", help="校验frontmatter + 密钥扫描")
    p_validate.add_argument("--fix", action="store_true", help="自动修正")

    # doctor
    p_doctor = subparsers.add_parser("doctor", help="一键巡检")
    p_doctor.add_argument("--fix", action="store_true", help="自动修正")

    # archive
    p_archive = subparsers.add_parser("archive", help="归档废弃skill")
    p_archive.add_argument("skill_id", help="Skill ID")

    # install
    p_install = subparsers.add_parser("install", help="从远程仓库安装skill")
    p_install.add_argument("skill_ids", nargs="*", help="要安装的skill ID（支持多个）")
    p_install.add_argument("--repo", default=DEFAULT_REMOTE, help=f"远程仓库 (默认: {DEFAULT_REMOTE})")
    p_install.add_argument("--dest", help="安装目标目录 (默认: skills/)")
    p_install.add_argument("--force", action="store_true", help="覆盖已存在的skill")
    p_install.add_argument("--list", dest="list_remote", action="store_true", help="列出远程可用skill")
    p_install.add_argument("--source", help="从本地仓库路径安装 (绕过网络下载)")
    p_install.add_argument("--token", help="GitHub API token (默认从gh auth获取)")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "status": cmd_status,
        "sync": cmd_sync,
        "pull": cmd_pull,
        "diff": cmd_diff,
        "init": cmd_init,
        "validate": cmd_validate,
        "doctor": cmd_doctor,
        "archive": cmd_archive,
        "install": cmd_install,
    }

    if args.command in commands:
        result = commands[args.command](args)
        sys.exit(result if isinstance(result, int) else 0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
