"""Clustta operators — actions triggered from UI panels."""

import bpy
from bpy.types import Operator

from . import api_client


class CLUSTTA_OT_ConnectAgent(Operator):
    """Connect to the Clustta Agent running on localhost."""

    bl_idname = "clustta.connect_agent"
    bl_label = "Connect to Agent"

    def execute(self, context):
        client = api_client.get_client()
        ok, err = client.health_check()
        clustta = context.scene.clustta

        if ok:
            clustta.agent_connected = True
            self.report({"INFO"}, "Connected to Clustta Agent")
        else:
            clustta.agent_connected = False
            self.report({"WARNING"}, f"Agent unreachable: {err}")

        return {"FINISHED"}


class CLUSTTA_OT_SwitchAccount(Operator):
    """Browse and switch the active Clustta account."""

    bl_idname = "clustta.switch_account"
    bl_label = "Switch Account"

    def execute(self, context):
        # TODO: show popup list of accounts from agent
        self.report({"INFO"}, "Account switching not yet implemented")
        return {"FINISHED"}


class CLUSTTA_OT_SwitchStudio(Operator):
    """Browse and switch the active studio."""

    bl_idname = "clustta.switch_studio"
    bl_label = "Switch Studio"

    def execute(self, context):
        # TODO: show popup list of studios from agent
        self.report({"INFO"}, "Studio switching not yet implemented")
        return {"FINISHED"}


class CLUSTTA_OT_SwitchProject(Operator):
    """Browse and switch the active project."""

    bl_idname = "clustta.switch_project"
    bl_label = "Switch Project"

    def execute(self, context):
        # TODO: show popup list of projects from agent
        self.report({"INFO"}, "Project switching not yet implemented")
        return {"FINISHED"}


class CLUSTTA_OT_RefreshAssets(Operator):
    """Refresh the asset list from the agent."""

    bl_idname = "clustta.refresh_assets"
    bl_label = "Refresh Assets"

    def execute(self, context):
        # TODO: call agent API to fetch assets filtered by .blend + assignee
        self.report({"INFO"}, "Asset refresh not yet implemented")
        return {"FINISHED"}


class CLUSTTA_OT_CreateCheckpoint(Operator):
    """Create a new checkpoint for the selected asset and sync push."""

    bl_idname = "clustta.create_checkpoint"
    bl_label = "Create Checkpoint"

    def execute(self, context):
        clustta = context.scene.clustta
        message = clustta.checkpoint_message

        if not message.strip():
            self.report({"WARNING"}, "Please enter a checkpoint message")
            return {"CANCELLED"}

        # TODO: call agent API to create checkpoint + push
        self.report({"INFO"}, f"Checkpoint creation not yet implemented: {message}")
        clustta.checkpoint_message = ""
        return {"FINISHED"}


# Registration
_classes = [
    CLUSTTA_OT_ConnectAgent,
    CLUSTTA_OT_SwitchAccount,
    CLUSTTA_OT_SwitchStudio,
    CLUSTTA_OT_SwitchProject,
    CLUSTTA_OT_RefreshAssets,
    CLUSTTA_OT_CreateCheckpoint,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
