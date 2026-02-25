"""Clustta operators — actions triggered from UI panels."""

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from . import api_client


# Dynamic enum caches (Blender requires the list to stay alive)
_account_items = []
_studio_items = []
_project_items = []


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

    def invoke(self, context, event):
        client = api_client.get_client()
        accounts, err = client.list_accounts()

        if err or not accounts:
            self.report({"WARNING"}, f"Could not load accounts: {err}")
            return {"CANCELLED"}

        global _account_items
        _account_items = [
            (a["id"], f'{a.get("first_name", "")} {a.get("last_name", "")} ({a["email"]})', "")
            for a in accounts
        ]

        context.window_manager.invoke_props_dialog(self)
        return {"RUNNING_MODAL"}

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

    def invoke(self, context, event):
        client = api_client.get_client()
        studios, err = client.list_studios()

        if err or not studios:
            self.report({"WARNING"}, f"Could not load studios: {err}")
            return {"CANCELLED"}

        global _studio_items
        _studio_items = [
            (s["name"], s["name"], s.get("url", ""))
            for s in studios
        ]

        context.window_manager.invoke_props_dialog(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        client = api_client.get_client()
        _, err = client.switch_studio(self.studio)

        if err:
            self.report({"WARNING"}, f"Failed to switch studio: {err}")
            return {"CANCELLED"}

        clustta = context.scene.clustta
        clustta.active_studio = self.studio
        clustta.active_studio_id = self.studio
        # Clear downstream selections
        clustta.active_project = ""
        clustta.active_project_id = ""
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

    def invoke(self, context, event):
        client = api_client.get_client()
        projects, err = client.list_projects()

        if err or not projects:
            self.report({"WARNING"}, f"Could not load projects: {err}")
            return {"CANCELLED"}

        global _project_items
        _project_items = [
            (p["uri"], p["name"], p.get("working_directory", ""))
            for p in projects
        ]

        context.window_manager.invoke_props_dialog(self)
        return {"RUNNING_MODAL"}

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
        self.report({"INFO"}, f"Switched to project: {name}")
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

        client = api_client.get_client()
        assets, err = client.get_assets(ext=".blend")

        if err:
            self.report({"WARNING"}, f"Failed to load assets: {err}")
            return {"CANCELLED"}

        # Clear and repopulate the asset collection
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

        self.report({"INFO"}, f"Loaded {len(clustta.assets)} assets")
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


def _sync_active_state(clustta, client):
    """Fetch active account and studio from the agent and update properties."""
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
    CLUSTTA_OT_CreateCheckpoint,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
