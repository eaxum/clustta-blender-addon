"""HTTP client for communicating with the Clustta Agent on localhost."""

import json
import urllib.request
import urllib.error
from typing import Any

AGENT_HOST = "http://127.0.0.1"
AGENT_PORT = 1173

_instance = None


class AgentClient:
    """Simple HTTP client wrapping the Clustta Agent REST API."""

    def __init__(self, host: str = AGENT_HOST, port: int = AGENT_PORT):
        self.base_url = f"{host}:{port}"

    def _request(self, method: str, path: str, body: dict | None = None) -> tuple[Any, str | None]:
        """Make an HTTP request to the agent. Returns (data, error)."""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
                return json.loads(content) if content else None, None
        except urllib.error.URLError as e:
            return None, str(e.reason)
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            return None, str(e)

    # Health
    def health_check(self) -> tuple[bool, str | None]:
        """Check if the agent is running."""
        data, err = self._request("GET", "/health")
        return err is None, err

    # Accounts
    def list_accounts(self) -> tuple[list | None, str | None]:
        """List accounts stored in the OS keyring."""
        return self._request("GET", "/accounts")

    def switch_account(self, account_id: str) -> tuple[Any, str | None]:
        """Set the active account."""
        return self._request("POST", "/accounts/switch", {"id": account_id})

    # Studios
    def list_studios(self) -> tuple[list | None, str | None]:
        """List studios for the active account."""
        return self._request("GET", "/studios")

    def switch_studio(self, studio_id: str) -> tuple[Any, str | None]:
        """Set the active studio."""
        return self._request("POST", "/studios/switch", {"id": studio_id})

    # Projects
    def list_projects(self) -> tuple[list | None, str | None]:
        """List projects in the active studio."""
        return self._request("GET", "/projects")

    def get_assets(self, project_id: str, ext: str = ".blend", assignee: str = "") -> tuple[list | None, str | None]:
        """Get assets filtered by extension and assignee."""
        params = f"?ext={ext}"
        if assignee:
            params += f"&assignee={assignee}"
        return self._request("GET", f"/projects/{project_id}/assets{params}")

    def get_checkpoints(self, project_id: str, asset_id: str) -> tuple[list | None, str | None]:
        """Get checkpoint history for an asset."""
        return self._request("GET", f"/projects/{project_id}/assets/{asset_id}/checkpoints")

    def create_checkpoint(self, project_id: str, asset_id: str, message: str, file_path: str) -> tuple[Any, str | None]:
        """Create a checkpoint and trigger sync push."""
        return self._request("POST", f"/projects/{project_id}/assets/{asset_id}/checkpoints", {
            "message": message,
            "filePath": file_path,
        })


def get_client() -> AgentClient:
    """Get or create the singleton agent client."""
    global _instance
    if _instance is None:
        _instance = AgentClient()
    return _instance
