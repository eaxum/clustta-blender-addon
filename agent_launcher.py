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


def is_agent_running() -> bool:
    """Check whether the agent is reachable on localhost."""
    client = api_client.get_client()
    ok, _ = client.health_check()
    return ok


def launch_agent() -> bool:
    """Attempt to start the bundled agent binary if it is not already running.

    Returns True if the agent is running (either already or newly started).
    """
    if is_agent_running():
        return True

    path = _bundled_agent_path()
    if not os.path.isfile(path):
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
