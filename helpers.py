"""Shared helper functions for loading data from the Clustta Agent."""

from datetime import datetime

from . import api_client

_loaded_assets_project_id = ""
_loaded_checkpoint_asset_id = ""

# File state icon mapping (Blender built-in icons)
FILE_STATE_ICONS = {
    "normal": "CHECKMARK",
    "outdated": "IMPORT",
    "modified": "GREASEPENCIL",
    "rebuildable": "FILE_REFRESH",
    "missing": "ERROR",
}
FILE_STATE_DEFAULT_ICON = "RADIOBUT_OFF"


def _format_timestamp(iso_str):
    """Convert an ISO 8601 timestamp to a short human-readable format (e.g. '4 Jan 26')."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return f"{dt.day} {dt.strftime('%b')} {dt.strftime('%y')}"
    except (ValueError, OSError):
        return iso_str


def load_assets(clustta):
    """Fetch assets from agent and populate the collection."""
    global _loaded_assets_project_id
    client = api_client.get_client()
    assets, err = client.get_assets(ext=".blend")

    if err:
        return False, err

    clustta.assets.clear()
    clustta.active_asset_index = -1

    for a in (assets or []):
        item = clustta.assets.add()
        item.asset_id = a.get("id", "")
        item.name = a.get("name", "")
        item.file_path = a.get("file_path", "")
        item.asset_type = a.get("task_type_name", "")
        item.status = a.get("status_short_name", "")
        item.file_state = a.get("file_status", "")

    _loaded_assets_project_id = clustta.active_project_id

    from . import props
    props.update_filter_items(clustta.assets)

    return True, None


def ensure_assets_loaded(clustta):
    """Load assets if not already loaded for the current project."""
    global _loaded_assets_project_id
    if _loaded_assets_project_id == clustta.active_project_id and len(clustta.assets) > 0:
        return
    load_assets(clustta)


def load_checkpoints(clustta, asset_id):
    """Fetch checkpoints for an asset and populate the collection."""
    global _loaded_checkpoint_asset_id
    client = api_client.get_client()
    checkpoints, err = client.get_checkpoints(asset_id)

    clustta.checkpoints.clear()
    clustta.active_checkpoint_index = -1

    if not err and checkpoints:
        for cp in checkpoints:
            item = clustta.checkpoints.add()
            item.checkpoint_id = cp.get("id", "")
            item.message = cp.get("comment", "")
            item.created_at = _format_timestamp(cp.get("created_at", ""))
            item.author = cp.get("author_id", "")

    _loaded_checkpoint_asset_id = asset_id


def ensure_checkpoints_loaded(clustta, asset_id):
    """Load checkpoints if not already loaded for the current asset."""
    global _loaded_checkpoint_asset_id
    if _loaded_checkpoint_asset_id == asset_id:
        return
    load_checkpoints(clustta, asset_id)


def reset_asset_cache():
    """Reset the asset cache when switching projects or studios."""
    global _loaded_assets_project_id
    _loaded_assets_project_id = ""


def reset_checkpoint_cache():
    """Reset the checkpoint cache when switching assets."""
    global _loaded_checkpoint_asset_id
    _loaded_checkpoint_asset_id = ""


def get_file_state_icon(file_state):
    """Return the Blender built-in icon name for a file state value."""
    return FILE_STATE_ICONS.get(file_state, FILE_STATE_DEFAULT_ICON)
