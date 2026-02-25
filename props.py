"""Clustta Blender properties - scene-level state for the addon."""

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup


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
    active_asset_index: IntProperty(name="Active Asset", default=-1)  # type: ignore[valid-type]

    # Checkpoint list
    checkpoints: CollectionProperty(type=ClusttaCheckpointItem)  # type: ignore[valid-type]
    active_checkpoint_index: IntProperty(name="Active Checkpoint", default=-1)  # type: ignore[valid-type]

    # Checkpoint creation
    checkpoint_message: StringProperty(name="Checkpoint Message", default="")  # type: ignore[valid-type]


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
