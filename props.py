"""Clustta Blender properties - scene-level state for the addon."""

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

# Filter enum item caches (must stay alive for Blender)
_asset_type_filter_items = [("ALL", "All Asset Types", "")]
_status_filter_items = [("ALL", "All Statuses", "")]


def _get_asset_type_items(self, context):
    """Return dynamic asset type filter items."""
    return _asset_type_filter_items


def _get_status_items(self, context):
    """Return dynamic status filter items."""
    return _status_filter_items


def update_filter_items(assets):
    """Rebuild filter enum items from loaded assets."""
    global _asset_type_filter_items, _status_filter_items

    types = set()
    statuses = set()
    for asset in assets:
        if asset.asset_type:
            types.add(asset.asset_type)
        if asset.status:
            statuses.add(asset.status)

    _asset_type_filter_items = [("ALL", "All Asset Types", "")]
    _asset_type_filter_items += [(t, t.title(), "") for t in sorted(types)]

    _status_filter_items = [("ALL", "All Statuses", "")]
    _status_filter_items += [(s, s.upper(), "") for s in sorted(statuses)]


class ClusttaAssetItem(PropertyGroup):
    """A single asset entry in the asset list."""

    asset_id: StringProperty(name="Asset ID", default="")  # type: ignore[valid-type]
    name: StringProperty(name="Name", default="")  # type: ignore[valid-type]
    file_path: StringProperty(name="File Path", default="")  # type: ignore[valid-type]
    asset_type: StringProperty(name="Asset Type", default="")  # type: ignore[valid-type]
    status: StringProperty(name="Status", default="")  # type: ignore[valid-type]
    file_state: StringProperty(name="File State", default="")  # type: ignore[valid-type]


class ClusttaCheckpointItem(PropertyGroup):
    """A single checkpoint entry in the checkpoint list."""

    checkpoint_id: StringProperty(name="Checkpoint ID", default="")  # type: ignore[valid-type]
    message: StringProperty(name="Message", default="")  # type: ignore[valid-type]
    created_at: StringProperty(name="Created At", default="")  # type: ignore[valid-type]
    author: StringProperty(name="Author", default="")  # type: ignore[valid-type]


def _on_asset_index_changed(self, context):
    """Called when the active asset selection changes."""
    from . import helpers
    clustta = context.scene.clustta
    if clustta.active_asset_index >= 0 and clustta.active_asset_index < len(clustta.assets):
        asset = clustta.assets[clustta.active_asset_index]
        helpers.reset_checkpoint_cache()
        helpers.load_checkpoints(clustta, asset.asset_id)


class ClusttaProperties(PropertyGroup):
    """Root property group attached to bpy.types.Scene."""

    # Agent connection
    agent_connected: BoolProperty(name="Agent Connected", default=False)  # type: ignore[valid-type]

    # Active selections (display strings)
    active_account: StringProperty(name="Active Account", default="")  # type: ignore[valid-type]
    active_account_id: StringProperty(name="Active Account ID", default="")  # type: ignore[valid-type]
    active_studio: StringProperty(name="Active Studio", default="")  # type: ignore[valid-type]
    active_studio_id: StringProperty(name="Active Studio ID", default="")  # type: ignore[valid-type]
    active_project: StringProperty(name="Active Project", default="")  # type: ignore[valid-type]
    active_project_id: StringProperty(name="Active Project ID", default="")  # type: ignore[valid-type]

    # Asset list
    assets: CollectionProperty(type=ClusttaAssetItem)  # type: ignore[valid-type]
    active_asset_index: IntProperty(name="Active Asset", default=-1, update=_on_asset_index_changed)  # type: ignore[valid-type]

    # Checkpoint list
    checkpoints: CollectionProperty(type=ClusttaCheckpointItem)  # type: ignore[valid-type]
    active_checkpoint_index: IntProperty(name="Active Checkpoint", default=-1)  # type: ignore[valid-type]

    # Checkpoint creation
    checkpoint_message: StringProperty(name="Checkpoint Message", default="")  # type: ignore[valid-type]

    # Filters
    filter_asset_type: EnumProperty(name="Asset Type", items=_get_asset_type_items)  # type: ignore[valid-type]
    filter_status: EnumProperty(name="Status", items=_get_status_items)  # type: ignore[valid-type]


# Registration
_classes = [
    ClusttaAssetItem,
    ClusttaCheckpointItem,
    ClusttaProperties,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.clustta = bpy.props.PointerProperty(type=ClusttaProperties)  # type: ignore[attr-defined]


def unregister():
    del bpy.types.Scene.clustta  # type: ignore[attr-defined]
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
