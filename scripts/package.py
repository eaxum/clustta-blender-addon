"""Package the Clustta Blender addon into a distributable .zip archive.

Usage:
    python scripts/package.py                           # addon-only (no agent binary)
    python scripts/package.py --agent PATH_TO_BINARY    # bundle agent binary

The script copies addon source files into a staging directory, optionally
copies the agent binary into bin/, and creates a .zip ready for Blender
installation.

Output: dist/clustta-blender-addon-<version>.zip
"""

import argparse
import os
import shutil
import sys
import tomllib
import zipfile

ADDON_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(ADDON_DIR, "dist")

# Files and directories to include in the package
INCLUDE_FILES = [
    "__init__.py",
    "agent_launcher.py",
    "api_client.py",
    "helpers.py",
    "operators.py",
    "panels.py",
    "props.py",
    "blender_manifest.toml",
    "LICENSE",
]

INCLUDE_DIRS = [
    "assets",
]

# Files/dirs to always exclude
EXCLUDE = {
    "__pycache__",
    ".git",
    ".gitignore",
    ".vscode",
    "scripts",
    "dist",
    "build",
    "*.pyc",
    "*.pyo",
}


def read_version() -> str:
    """Read the addon version from blender_manifest.toml."""
    manifest_path = os.path.join(ADDON_DIR, "blender_manifest.toml")
    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)
    return manifest.get("version", "0.0.0")


def package(agent_binary: str | None = None) -> str:
    """Build the addon .zip archive and return its path."""
    version = read_version()
    archive_name = f"clustta-blender-addon-{version}"
    staging_dir = os.path.join(DIST_DIR, "clustta")

    # Clean previous build
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir, exist_ok=True)

    # Copy addon source files
    for filename in INCLUDE_FILES:
        src = os.path.join(ADDON_DIR, filename)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(staging_dir, filename))

    # Copy addon directories
    for dirname in INCLUDE_DIRS:
        src = os.path.join(ADDON_DIR, dirname)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(staging_dir, dirname))

    # Bundle agent binary if provided
    if agent_binary:
        if not os.path.isfile(agent_binary):
            print(f"Error: Agent binary not found: {agent_binary}", file=sys.stderr)
            sys.exit(1)
        bin_dir = os.path.join(staging_dir, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        dest = os.path.join(bin_dir, os.path.basename(agent_binary))
        shutil.copy2(agent_binary, dest)
        print(f"  Bundled agent: {agent_binary} -> bin/{os.path.basename(agent_binary)}")

    # Create .zip
    zip_path = os.path.join(DIST_DIR, f"{archive_name}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(staging_dir):
            # Filter out excluded dirs in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
            for filename in files:
                if filename in EXCLUDE:
                    continue
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, DIST_DIR)
                zf.write(filepath, arcname)

    # Clean staging
    shutil.rmtree(staging_dir)

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"  Package: {zip_path} ({size_mb:.1f} MB)")
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Package the Clustta Blender addon")
    parser.add_argument(
        "--agent",
        metavar="PATH",
        help="Path to the clustta-agent binary to bundle (e.g. ../clustta-client/bin/clustta-agent.exe)",
    )
    args = parser.parse_args()

    print(f"Packaging Clustta Blender Addon v{read_version()}...")
    package(agent_binary=args.agent)
    print("Done.")


if __name__ == "__main__":
    main()
