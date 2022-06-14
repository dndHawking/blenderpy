"""
WIP for the Blender Extensions
"""

import bpy


class Remove(bpy.types.Operator):
    """Remove selected objects"""

    bl_idname = "object.remove"
    bl_label = "Remove"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.selected_objects:
            bpy.data.objects.remove(obj)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Remove selected objects")
