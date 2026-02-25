"""Clustta operators — actions triggered from UI panels."""

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from . import api_client, helpers


# Dynamic enum caches (Blender requires the list to stay alive)
_account_items = [("__NONE__", "No accounts loaded", "")]
_studio_items = [("__NONE__", "No studios loaded", "")]
_project_items = [("__NONE__", "No projects loaded", "")]


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
            # Load the active account and studio on connect
            _sync_active_state(clustta, client)
            self.report({"INFO"}, "Connected to Clustta Agent")
        else:
            clustta.agent_connected = False
            self.report({"WARNING"}, f"Agent unreachable: {err}")

        return {"FINISHED"}


class CLUSTTA_OT_SwitchAccount(Operator):
    """Browse and switch the active Clustta account."""

    bl_idname = "clustta.switch_account"
    bl_label = "Switch Account"

    account: EnumProperty(  # type: ignore[valid-type]
        name="Account",
        description="Select an account",
        items=lambda self, context: _account_items,
    )

    def execute(self, context):
        client = api_client.get_client()
        _, err = client.switch_account(self.account)

        if err:
            self.report({"WARNING"}, f"Failed to switch account: {err}")
            return {"CANCELLED"}

        # Refresh active state
        clustta = context.scene.clustta
        _sync_active_state(clustta, client)
        self.report({"INFO"}, f"Switched to {clustta.active_account}")
        return {"FINISHED"}


class CLUSTTA_OT_SwitchStudio(Operator):
    """Browse and switch the active studio."""

    bl_idname = "clustta.switch_studio"
    bl_label = "Switch Studio"

    studio: EnumProperty(  # type: ignore[valid-type]
        name="Studio",
        description="Select a studio",
        items=lambda self, context: _studio_items,
    )

    def execute(self, context):
        client = api_client.get_client()
        _, err = client.switch_studio(self.studio)

        if err:
            self.report({"WARNING"}, f"Failed to switch studio: {err}")
            return {"CANCELLED"}

        clustta = context.scene.clustta
        clustta.active_studio = self.studio
        clustta.active_studio_id = self.studio
        # Clear downstream selections and caches
        clustta.active_project = ""
        clustta.active_project_id = ""
        clustta.assets.clear()
        clustta.checkpoints.clear()
        helpers.reset_asset_cache()
        helpers.reset_checkpoint_cache()
        _refresh_project_items(client)
        self.report({"INFO"}, f"Switched to studio: {self.studio}")
        return {"FINISHED"}


class CLUSTTA_OT_SwitchProject(Operator):
    """Browse and switch the active project."""

    bl_idname = "clustta.switch_project"
    bl_label = "Switch Project"

    project: EnumProperty(  # type: ignore[valid-type]
        name="Project",
        description="Select a project",
        items=lambda self, context: _project_items,
    )

    def execute(self, context):
        client = api_client.get_client()
        _, err = client.switch_project(self.project)

        if err:
            self.report({"WARNING"}, f"Failed to switch project: {err}")
            return {"CANCELLED"}

        # Find display name from cached items
        name = self.project
        for uri, label, _ in _project_items:
            if uri == self.project:
                name = label
                break

        clustta = context.scene.clustta
        clustta.active_project = name
        clustta.active_project_id = self.project

        # Load assets for the new project
        helpers.reset_asset_cache()
        helpers.reset_checkpoint_cache()
        ok, _ = helpers.load_assets(clustta)
        count = len(clustta.assets) if ok else 0
        self.report({"INFO"}, f"Switched to project: {name} ({count} assets)")
        return {"FINISHED"}


class CLUSTTA_OT_RefreshAssets(Operator):
    """Refresh the asset list from the agent."""

    bl_idname = "clustta.refresh_assets"
    bl_label = "Refresh Assets"

    def execute(self, context):
        clustta = context.scene.clustta

        if not clustta.active_project_id:
            self.report({"WARNING"}, "No project selected")
            return {"CANCELLED"}

        helpers.reset_asset_cache()
        ok, err = helpers.load_assets(clustta)

        if not ok:
            self.report({"WARNING"}, f"Failed to load assets: {err}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Loaded {len(clustta.assets)} assets")
        return {"FINISHED"}


class CLUSTTA_OT_RefreshCheckpoints(Operator):
    """Reload checkpoints for the selected asset."""

    bl_idname = "clustta.refresh_checkpoints"
    bl_label = "Refresh Checkpoints"

    def execute(self, context):
        clustta = context.scene.clustta

        if clustta.active_asset_index < 0 or clustta.active_asset_index >= len(clustta.assets):
            self.report({"WARNING"}, "No asset selected")
            return {"CANCELLED"}

        asset = clustta.assets[clustta.active_asset_index]
        helpers.reset_checkpoint_cache()
        helpers.load_checkpoints(clustta, asset.asset_id)
        self.report({"INFO"}, f"Loaded {len(clustta.checkpoints)} checkpoints")
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

        # Checkpoint creation requires Phase 7 agent endpoints
        self.report({"INFO"}, f"Checkpoint creation not yet implemented: {message}")
        clustta.checkpoint_message = ""
        return {"FINISHED"}


def _refresh_account_items(client):
    """Populate the account selector items from the agent."""
    global _account_items
    accounts, err = client.list_accounts()
    if not err and accounts:
        _account_items = [
            (a["id"], f'{a.get("first_name", "")} {a.get("last_name", "")} ({a["email"]})', "")
            for a in accounts
        ]


def _refresh_studio_items(client):
    """Populate the studio selector items from the agent."""
    global _studio_items
    studios, err = client.list_studios()
    if not err and studios:
        _studio_items = [
            (s["name"], s["name"], s.get("url", ""))
            for s in studios
        ]


def _refresh_project_items(client):
    """Populate the project selector items from the agent."""
    global _project_items
    projects, err = client.list_projects()
    if not err and projects:
        _project_items = [
            (p["uri"], p["name"], p.get("working_directory", ""))
            for p in projects
        ]


def _sync_active_state(clustta, client):
    """Fetch active state from the agent and populate selector caches."""
    _refresh_account_items(client)
    _refresh_studio_items(client)
    _refresh_project_items(client)

    active, err = client.get_active_account()
    if not err and active:
        name = f'{active.get("first_name", "")} {active.get("last_name", "")}'.strip()
        clustta.active_account = name or active.get("email", "")
        clustta.active_account_id = active.get("id", "")

    studio, err = client.get_active_studio()
    if not err and studio:
        clustta.active_studio = studio.get("name", "")
        clustta.active_studio_id = studio.get("name", "")

    project, err = client.get_active_project()
    if not err and project:
        clustta.active_project = project.get("name", "")
        clustta.active_project_id = project.get("uri", "")


# Registration
_classes = [
    CLUSTTA_OT_ConnectAgent,
    CLUSTTA_OT_SwitchAccount,
    CLUSTTA_OT_SwitchStudio,
    CLUSTTA_OT_SwitchProject,
    CLUSTTA_OT_RefreshAssets,
    CLUSTTA_OT_RefreshCheckpoints,
    CLUSTTA_OT_CreateCheckpoint,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
