#!/usr/bin/env python3
"""Validate course assets in temporary directories, without cloud operations."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TERRAFORM = os.environ.get("TERRAFORM_BIN", "terraform")


def run(*args, cwd=ROOT):
    print("+ " + " ".join(str(arg) for arg in args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def check_links():
    checked = 0
    for path in ROOT.rglob("*.md"):
        if ".terraform" in path.parts:
            continue
        text = path.read_text()
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                raise ValueError(f"Broken local Markdown link: {path.relative_to(ROOT)} -> {target}")
            checked += 1
    print(f"Checked {checked} local Markdown links.", flush=True)


def copy_example(source, destination):
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(
        ".terraform", ".terraform.lock.hcl", "*.tfstate", "*.tfstate.*", "__pycache__"
    ))


def terraform_checks(directory, test=False, readonly=False):
    init = [TERRAFORM, "init", "-backend=false", "-input=false", "-no-color"]
    if readonly:
        init.append("-lockfile=readonly")
    run(*init, cwd=directory)
    run(TERRAFORM, "validate", "-no-color", cwd=directory)
    if test:
        run(TERRAFORM, "test", "-no-color", cwd=directory)


def main():
    check_links()
    run(TERRAFORM, "fmt", "-check", "-recursive")
    workflow_paths = sorted(ROOT.glob(".github/workflows/*.yml")) + sorted(ROOT.glob("templates/*.yml"))
    run("ruby", "-e", "require 'yaml'; ARGV.each { |p| YAML.load_file(p); puts \"YAML OK: #{p}\" }",
        *(str(path) for path in workflow_paths))
    run(sys.executable, "-m", "unittest", "discover", "-s", "templates/tests", "-v")

    with tempfile.TemporaryDirectory(prefix="terraform-course-check-") as scratch:
        scratch = Path(scratch)
        if "TF_PLUGIN_CACHE_DIR" not in os.environ:
            cache = scratch / "provider-cache"
            cache.mkdir()
            os.environ["TF_PLUGIN_CACHE_DIR"] = str(cache)
        rg = scratch / "resource-group"
        network = scratch / "network"
        upgraded = scratch / "network-v1.1.0"
        live = scratch / "dev"
        copy_example(ROOT / "examples/resource-group-module", rg)
        copy_example(ROOT / "examples/network-module", network)
        copy_example(ROOT / "examples/network-module", upgraded)
        copy_example(ROOT / "examples/live/environments/dev", live)
        delta = ROOT / "examples/network-module-v1.1.0"
        shutil.copy2(delta / "outputs-addition.tf", upgraded / "outputs-addition.tf")
        shutil.copy2(delta / "upgrade.tftest.hcl", upgraded / "tests/upgrade.tftest.hcl")
        for directory in (rg, network, upgraded, live):
            shutil.copy2(ROOT / "examples/live/environments/dev/.terraform.lock.hcl",
                         directory / ".terraform.lock.hcl")

        text = (live / "main.tf").read_text()
        for repository, local in [("resource-group", rg), ("network", network)]:
            source = f"git::https://github.com/YOUR_GITHUB_USER/terraform-azurerm-{repository}.git?ref=v1.0.0"
            if text.count(source) != 1:
                raise ValueError(f"Expected exactly one v1.0.0 {repository} Git source in live baseline.")
            text = text.replace(source, local.as_posix())
        (live / "main.tf").write_text(text)

        terraform_checks(rg, test=True, readonly=True)
        terraform_checks(network, test=True, readonly=True)
        terraform_checks(upgraded, test=True, readonly=True)
        terraform_checks(live, readonly=True)

        # Also validate the exact additive consumer upgrade from lesson 09.
        (live / "main.tf").write_text(text.replace(network.as_posix() + '"', upgraded.as_posix() + '"'))
        with (live / "outputs.tf").open("a") as output:
            output.write('\noutput "subnet_names" {\n  value = module.network.subnet_names\n}\n')
        terraform_checks(live, readonly=True)
    print("All course checks passed. No Azure plan/apply or HCP API calls were made.", flush=True)


if __name__ == "__main__":
    main()
