#!/usr/bin/env python3
"""
Upload OpenCode Ecosystem Core to HuggingFace Hub.
Mirror repository structure like GitHub.

Usage:
    python3 scripts/upload_to_hf_hub.py

Rate limit: 128 commits/hour (free plan). Wait 40 min if 429 error.
Repo: https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core
"""

import os
import time
import shutil
from huggingface_hub import HfApi

TOKEN = os.environ.get("HF_TOKEN", "hf_***REDACTED***")
REPO = "marceloclaro/opencode-ecosystem-core"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING = "/tmp/hf_staging"


def prepare_staging():
    """Copy key files to staging directory."""
    if os.path.exists(STAGING):
        shutil.rmtree(STAGING)
    os.makedirs(STAGING)

    # Root docs
    root_docs = [
        "README.md", "ARCHITECTURE.md", "AGENTS.md", "CLAUDE.md", "MANUAL.md",
        "CONTRIBUTING.md", "SECURITY.md", "LICENSE", "CHANGELOG.md", "CORRIGENDUM.md",
        "PROGRESS.md", "RELEASE_NOTES.md", "requirements.txt", "requirements-dev.txt",
        "requirements-scientific-lab.txt", "setup.cfg", "pytest.ini", "opencode.json",
        ".gitignore",
    ]
    for f in root_docs:
        src = os.path.join(BASE, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(STAGING, f))

    # Core modules
    core_dirs = [
        "marceloclaro", "academic", "research", "evolution", "sdd", "scanner",
        "transformer", "trust", "translation", "mci", "reasoning", "gametheory",
        "economy", "integrations", "scripts", "scientific_lab",
    ]
    for d in core_dirs:
        src = os.path.join(BASE, d)
        if os.path.exists(src):
            shutil.copytree(
                src, os.path.join(STAGING, d),
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                dirs_exist_ok=True,
            )

    # Data
    os.makedirs(os.path.join(STAGING, "data"), exist_ok=True)
    for f in ["research_proposals.json", "scientific_datasets_catalog.json", "phd_agents.json"]:
        src = os.path.join(BASE, "data", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(STAGING, "data", f))

    # Agents catalog (first 50)
    agents_src = os.path.join(BASE, "agents", "catalog")
    if os.path.exists(agents_src):
        dst = os.path.join(STAGING, "agents", "catalog")
        os.makedirs(dst, exist_ok=True)
        for af in sorted(os.listdir(agents_src))[:50]:
            if af.endswith(".md"):
                shutil.copy2(os.path.join(agents_src, af), os.path.join(dst, af))

    # Specs (first 50)
    specs_src = os.path.join(BASE, "specs")
    if os.path.exists(specs_src):
        dst = os.path.join(STAGING, "specs")
        os.makedirs(dst, exist_ok=True)
        for sf in sorted(os.listdir(specs_src))[:50]:
            if sf.endswith(".md"):
                shutil.copy2(os.path.join(specs_src, sf), os.path.join(dst, sf))

    # Skills
    skills_src = os.path.join(BASE, ".opencode", "skills")
    if os.path.exists(skills_src):
        shutil.copytree(
            skills_src, os.path.join(STAGING, ".opencode", "skills"),
            dirs_exist_ok=True,
        )

    # Docs
    docs_src = os.path.join(BASE, "docs")
    if os.path.exists(docs_src):
        shutil.copytree(
            docs_src, os.path.join(STAGING, "docs"),
            ignore=shutil.ignore_patterns("__pycache__"),
            dirs_exist_ok=True,
        )

    # Tests (first 50)
    tests_src = os.path.join(BASE, "tests")
    if os.path.exists(tests_src):
        dst = os.path.join(STAGING, "tests")
        os.makedirs(dst, exist_ok=True)
        for tf in sorted(os.listdir(tests_src))[:50]:
            if tf.endswith(".py"):
                shutil.copy2(os.path.join(tests_src, tf), os.path.join(dst, tf))

    # Examples
    examples_src = os.path.join(BASE, "examples")
    if os.path.exists(examples_src):
        shutil.copytree(
            examples_src, os.path.join(STAGING, "examples"),
            ignore=shutil.ignore_patterns("__pycache__"),
            dirs_exist_ok=True,
        )

    count = sum(1 for _, _, files in os.walk(STAGING) for _ in files)
    size_mb = sum(
        os.path.getsize(os.path.join(r, f))
        for r, _, files in os.walk(STAGING)
        for f in files
    ) / 1024 / 1024
    print(f"Staging prepared: {count} files, {size_mb:.1f} MB")
    return count


def upload():
    """Upload staging directory to HuggingFace Hub."""
    api = HfApi(token=TOKEN)

    # Ensure repo exists
    api.create_repo(repo_id=REPO, repo_type="dataset", exist_ok=True)

    print(f"Uploading to {REPO}...")
    start = time.time()

    try:
        api.upload_folder(
            folder_path=STAGING,
            repo_id=REPO,
            repo_type="dataset",
            commit_message="Mirror: OpenCode Ecosystem Core - full repository",
        )
        elapsed = time.time() - start
        print(f"✅ Upload complete in {elapsed:.1f}s")
        return True
    except Exception as e:
        elapsed = time.time() - start
        err = str(e)
        if "429" in err:
            print(f"⏳ Rate limited after {elapsed:.1f}s. Wait 40 min and retry.")
            print("   Or upgrade to paid plan: https://huggingface.co/pricing")
            return False
        else:
            print(f"❌ Error after {elapsed:.1f}s: {e}")
            return False


if __name__ == "__main__":
    prepare_staging()
    upload()
