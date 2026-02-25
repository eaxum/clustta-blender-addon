"""Auto-launch the Clustta Agent if it is not already running."""

import os
import platform
import subprocess

from . import api_client


def _default_agent_path() -> str:
    """Return the platform-specific default path for the agent binary."""
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Clustta", "clustta-agent.exe")
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

    Returns True if the agent is running (either already or newly started).
    """
    if is_agent_running():
        return True

    path = agent_path or _default_agent_path()
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
