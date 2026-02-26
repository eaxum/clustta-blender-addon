"""HTTP client for communicating with the Clustta Bridge on localhost."""

import json
import urllib.request
import urllib.error
from typing import Any

BRIDGE_HOST = "http://127.0.0.1"
BRIDGE_PORT = 1173

_instance = None


class BridgeClient:
    """Simple HTTP client wrapping the Clustta Bridge REST API."""

    def __init__(self, host: str = BRIDGE_HOST, port: int = BRIDGE_PORT):
        self.base_url = f"{host}:{port}"

    def _request(self, method: str, path: str, body: dict | None = None) -> tuple[Any, str | None]:
        """Make an HTTP request to the bridge. Returns (data, error)."""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                content = resp.read().decode("utf-8")
                return json.loads(content) if content else None, None
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError:
            return None, "Check if Clustta is running"
        except (TimeoutError, OSError):
            return None, "Check if Clustta is running"
        except Exception as e:
            return None, str(e)

    # Health
    def health_check(self) -> tuple[bool, str | None]:
        """Check if the bridge is reachable."""
        data, err = self._request("GET", "/health")
        return err is None, err

    # Accounts
    def list_accounts(self) -> tuple[list | None, str | None]:
        """List accounts stored in the OS keyring."""
        return self._request("GET", "/accounts")

    def switch_account(self, account_id: str) -> tuple[Any, str | None]:
        """Set the active account."""
        return self._request("POST", "/accounts/switch", {"id": account_id})

    def get_active_account(self) -> tuple[dict | None, str | None]:
        """Get the currently active account."""
        return self._request("GET", "/accounts/active")

    # Studios
    def list_studios(self) -> tuple[list | None, str | None]:
        """List studios for the active account."""
        return self._request("GET", "/studios")

    def switch_studio(self, studio_name: str) -> tuple[Any, str | None]:
        """Set the active studio by name."""
        return self._request("POST", "/studios/switch", {"name": studio_name})

    def get_active_studio(self) -> tuple[dict | None, str | None]:
        """Get the currently active studio."""
        return self._request("GET", "/studios/active")

    # Projects
    def list_projects(self) -> tuple[list | None, str | None]:
        """List projects in the active studio."""
        return self._request("GET", "/projects")

    def switch_project(self, project_uri: str) -> tuple[Any, str | None]:
        """Set the active project by URI."""
        return self._request("POST", "/projects/switch", {"uri": project_uri})

    def get_active_project(self) -> tuple[dict | None, str | None]:
        """Get the currently active project."""
        return self._request("GET", "/projects/active")

    def get_assets(self, ext: str = ".blend") -> tuple[list | None, str | None]:
        """Get assets for the active project, filtered by extension."""
        params = f"?ext={ext}" if ext else ""
        return self._request("GET", f"/assets{params}")

    def get_checkpoints(self, asset_id: str) -> tuple[list | None, str | None]:
        """Get checkpoint history for an asset in the active project."""
        return self._request("GET", f"/assets/{asset_id}/checkpoints")

    def create_checkpoint(self, project_id: str, asset_id: str, message: str, file_path: str) -> tuple[Any, str | None]:
        """Create a checkpoint and trigger sync push."""
        return self._request("POST", f"/projects/{project_id}/assets/{asset_id}/checkpoints", {
            "message": message,
            "filePath": file_path,
        })


def get_client() -> BridgeClient:
    """Get or create the singleton bridge client."""
    global _instance
    if _instance is None:
        _instance = BridgeClient()
    return _instance
