"""Auto-launch the Clustta Agent if it is not already running."""

import os
import platform
import subprocess

from . import api_client

_AGENT_BINARY = "clustta-agent.exe" if platform.system() == "Windows" else "clustta-agent"


def _bundled_agent_path() -> str:
    """Return the path to the agent binary bundled inside the addon's bin/ directory."""
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(addon_dir, "bin", _AGENT_BINARY)


def _system_agent_path() -> str:
    """Return the platform-specific system install path for the agent binary."""
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Clustta", _AGENT_BINARY)
    elif system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Clustta/clustta-agent")
    else:
        return os.path.expanduser("~/.local/bin/clustta-agent")


def is_agent_running() -> bool:
    """Check whether the agent is reachable on localhost."""
    client = api_client.get_client()
    ok, _ = client.health_check()
    return ok


def launch_agent(agent_path: str | None = None) -> bool:
    """Attempt to start the agent process if it is not already running.

    Looks for the binary in this order: explicit path, bundled bin/, system install.
    Returns True if the agent is running (either already or newly started).
    """
    if is_agent_running():
        return True

    # Resolution order: explicit > bundled > system
    candidates = [agent_path, _bundled_agent_path(), _system_agent_path()]
    path = None
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            path = candidate
            break

    if path is None:
        return False

    try:
        kwargs = {}
        if platform.system() == "Windows":
            # Hide the console window on Windows
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = si

        subprocess.Popen(
            [path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **kwargs,
        )
        return True
    except OSError:
        return False
