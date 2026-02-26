"""Clustta UI panels for the Blender 3D Viewport sidebar."""

import bpy
from bpy.types import Context, Panel, UILayout

from . import helpers


class CLUSTTA_PT_Main(Panel):
    """Main Clustta panel in the 3D Viewport sidebar."""

    bl_label = "Clustta"
    bl_idname = "CLUSTTA_PT_Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Clustta"

    def draw(self, context: Context) -> None:
        layout = self.layout
        clustta = context.scene.clustta

        if not clustta.bridge_connected:
            row = layout.row()
            row.alert = True
            row.label(text="Clustta app not connected", icon="ERROR")
            layout.operator("clustta.connect_bridge", icon="FILE_REFRESH")
            return

        # Account row
        row = layout.split(factor=0.3)
        row.label(text="Account")
        row.operator_menu_enum("clustta.switch_account", "account", text=clustta.active_account or "Select Account", icon="DOWNARROW_HLT")

        # Studio row
        if clustta.active_account:
            row = layout.split(factor=0.3)
            row.label(text="Studio")
            row.operator_menu_enum("clustta.switch_studio", "studio", text=clustta.active_studio or "Select Studio", icon="DOWNARROW_HLT")

        # Project row
        if clustta.active_studio:
            row = layout.split(factor=0.3)
            row.label(text="Project")
            row.operator_menu_enum("clustta.switch_project", "project", text=clustta.active_project or "Select Project", icon="DOWNARROW_HLT")


class CLUSTTA_PT_Assets(Panel):
    """Asset browser panel, shown when a project is active."""

    bl_label = "Your Tasks"
    bl_idname = "CLUSTTA_PT_Assets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Clustta"
    bl_parent_id = "CLUSTTA_PT_Main"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return bool(context.scene.clustta.active_project)

    def draw(self, context: Context) -> None:
        layout = self.layout
        clustta = context.scene.clustta

        # Auto-load assets on first expand
        helpers.ensure_assets_loaded(clustta)

        # Filter dropdowns + reload button
        row = layout.row(align=True)
        row.prop(clustta, "filter_asset_type", text="")
        row.prop(clustta, "filter_status", text="")
        row.operator("clustta.refresh_assets", icon="FILE_REFRESH", text="")

        # Asset list
        layout.template_list(
            "CLUSTTA_UL_Assets", "",
            clustta, "assets",
            clustta, "active_asset_index",
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

    @classmethod
    def poll(cls, context: Context) -> bool:
        clustta = context.scene.clustta
        return bool(clustta.active_project) and clustta.active_asset_index >= 0

    def draw(self, context: Context) -> None:
        layout = self.layout
        clustta = context.scene.clustta

        # Header row with count and reload button
        row = layout.row()
        row.label(text=f"{len(clustta.checkpoints)} checkpoint(s)")
        row.operator("clustta.refresh_checkpoints", icon="FILE_REFRESH", text="")

        # Checkpoint list
        layout.template_list(
            "CLUSTTA_UL_Checkpoints", "",
            clustta, "checkpoints",
            clustta, "active_checkpoint_index",
            rows=4,
        )

        # Create checkpoint
        box = layout.box()
        box.prop(clustta, "checkpoint_message", text="Message")
        box.operator("clustta.create_checkpoint", icon="CHECKMARK")


class CLUSTTA_UL_Assets(bpy.types.UIList):
    """UI list for displaying assets with status and file state."""

    bl_idname = "CLUSTTA_UL_Assets"

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            split = layout.split(factor=0.6)
            split.label(text=item.name, icon="BLENDER")

            row = split.row(align=True)
            row.alignment = "RIGHT"
            if item.status:
                row.label(text=item.status.upper())
            state_icon = helpers.get_file_state_icon(item.file_state)
            row.label(text="", icon=state_icon)

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon="BLENDER")

    def filter_items(self, context, data, propname):
        """Filter assets by asset type and status dropdowns."""
        items = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(items)
        flt_neworder = list(range(len(items)))

        clustta = context.scene.clustta
        type_filter = clustta.filter_asset_type
        status_filter = clustta.filter_status

        for i, item in enumerate(items):
            if type_filter != "ALL" and item.asset_type != type_filter:
                flt_flags[i] = 0
            if status_filter != "ALL" and item.status != status_filter:
                flt_flags[i] = 0

        return flt_flags, flt_neworder


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
