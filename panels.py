"""Clustta UI panels for the Blender 3D Viewport sidebar."""

import bpy
from bpy.types import Context, Panel, UILayout


class CLUSTTA_PT_Main(Panel):
    """Main Clustta panel in the 3D Viewport sidebar."""

    bl_label = "Clustta"
    bl_idname = "CLUSTTA_PT_Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Clustta"

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        clustta = scene.clustta

        # Agent connection status
        if not clustta.agent_connected:
            row = layout.row()
            row.alert = True
            row.label(text="Agent not connected", icon="ERROR")
            layout.operator("clustta.connect_agent", icon="FILE_REFRESH")
            return

        # Account section
        self._draw_account_section(layout, clustta)

        # Studio section
        if clustta.active_account:
            self._draw_studio_section(layout, clustta)

        # Project section
        if clustta.active_studio:
            self._draw_project_section(layout, clustta)

    def _draw_account_section(self, layout: UILayout, clustta) -> None:
        """Draw the account switcher row."""
        box = layout.box()
        row = box.row()
        row.label(text="Account", icon="USER")

        if clustta.active_account:
            row.label(text=clustta.active_account)
        else:
            row.label(text="No account selected")

        box.operator("clustta.switch_account", icon="DOWNARROW_HLT")

    def _draw_studio_section(self, layout: UILayout, clustta) -> None:
        """Draw the studio switcher row."""
        box = layout.box()
        row = box.row()
        row.label(text="Studio", icon="COMMUNITY")

        if clustta.active_studio:
            row.label(text=clustta.active_studio)
        else:
            row.label(text="No studio selected")

        box.operator("clustta.switch_studio", icon="DOWNARROW_HLT")

    def _draw_project_section(self, layout: UILayout, clustta) -> None:
        """Draw the project switcher row."""
        box = layout.box()
        row = box.row()
        row.label(text="Project", icon="FILE_FOLDER")

        if clustta.active_project:
            row.label(text=clustta.active_project)
        else:
            row.label(text="No project selected")

        box.operator("clustta.switch_project", icon="DOWNARROW_HLT")


class CLUSTTA_PT_Assets(Panel):
    """Asset browser panel, shown when a project is active."""

    bl_label = "Assets"
    bl_idname = "CLUSTTA_PT_Assets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Clustta"
    bl_parent_id = "CLUSTTA_PT_Main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return bool(context.scene.clustta.active_project)

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("clustta.refresh_assets", icon="FILE_REFRESH", text="")
        row.label(text="Blender Assets")

        # Asset list
        layout.template_list(
            "CLUSTTA_UL_Assets", "",
            scene.clustta, "assets",
            scene.clustta, "active_asset_index",
            rows=6,
        )


class CLUSTTA_PT_Checkpoints(Panel):
    """Checkpoint history panel for the selected asset."""

    bl_label = "Checkpoints"
    bl_idname = "CLUSTTA_PT_Checkpoints"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Clustta"
    bl_parent_id = "CLUSTTA_PT_Main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        clustta = context.scene.clustta
        return bool(clustta.active_project) and clustta.active_asset_index >= 0

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene

        # Checkpoint list
        layout.template_list(
            "CLUSTTA_UL_Checkpoints", "",
            scene.clustta, "checkpoints",
            scene.clustta, "active_checkpoint_index",
            rows=4,
        )

        # Create checkpoint
        box = layout.box()
        box.prop(scene.clustta, "checkpoint_message", text="Message")
        box.operator("clustta.create_checkpoint", icon="CHECKMARK")


class CLUSTTA_UL_Assets(bpy.types.UIList):
    """UI list for displaying assets."""

    bl_idname = "CLUSTTA_UL_Assets"

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name, icon="FILE_BLEND")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon="FILE_BLEND")


class CLUSTTA_UL_Checkpoints(bpy.types.UIList):
    """UI list for displaying checkpoints."""

    bl_idname = "CLUSTTA_UL_Checkpoints"

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.label(text=item.message, icon="RECOVER_LAST")
            row.label(text=item.created_at)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon="RECOVER_LAST")


# Registration
_classes = [
    CLUSTTA_UL_Assets,
    CLUSTTA_UL_Checkpoints,
    CLUSTTA_PT_Main,
    CLUSTTA_PT_Assets,
    CLUSTTA_PT_Checkpoints,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
