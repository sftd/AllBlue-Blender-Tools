# ab_addons_tools.py Copyright (C) 2012, Jakub Zolcik
#
# Searches through files in file browser by name.
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Add-ons Tools",
    "author": "Jakub Zolcik",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "File",
    "description": "Allows enabling add-ons according to *.blend files.",
    "warning": "",
    "wiki_url": "https://studio.allblue.pl/wiki/wikis/blender/addons-tools",
    "tracker_url": "https://github.com/sftd/AllBlue-Blender-Tools",
    "category": "System"
}


import bpy
import addon_utils
from bpy.app.handlers import persistent


class AddonsToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    load = bpy.props.BoolProperty('Load Add-ons automatically', default=True)
    
    def draw(self, context):
        layout = self.layout
        layout.label('Addons Tools Preferences')
        layout.prop(self, 'load', text='Load Add-ons automatically')


class ADTAddonItem(bpy.types.PropertyGroup):
    module = bpy.props.StringProperty(name="Module", default='')
    

def adt_enable_addons():
    context = bpy.context
    scene = bpy.data.scenes[0]

    enabled_addons = context.user_preferences.addons.keys()

    for adt_addon in scene.adt_addons:
        if (adt_addon.module not in enabled_addons):
            bpy.ops.wm.addon_enable(module=adt_addon.module)

    
class ADTEnableAddonsOperator(bpy.types.Operator):
    bl_idname = "wm.adt_enable_addons"
    bl_label = "ADT Enable Add-ons"

    def execute(self, context):
        adt_enable_addons()
        return {"FINISHED"}


def adt_menu_draw(self, context):
    self.layout.operator("wm.adt_enable_addons", icon='LOAD_FACTORY')
    if (context.window_manager.adt_save):
        self.layout.prop(context.window_manager, "adt_save", text="ADT Save Add-ons", icon='CHECKBOX_HLT')
    else:
        self.layout.prop(context.window_manager, "adt_save", text="ADT Save Add-ons", icon='CHECKBOX_DEHLT')
    self.layout.separator()


def adt_save_update(self, context):
    scene = bpy.data.scenes[0]
    scene.adt_save = context.window_manager.adt_save

@persistent
def adt_save_pre_handler(dummy):
    context = bpy.context
    scene = bpy.data.scenes[0]

    scene.adt_save = context.window_manager.adt_save

    scene.adt_addons.clear()

    if (not context.window_manager.adt_save):
        return

    for addon in context.user_preferences.addons:
        adt_addon = scene.adt_addons.add()
        adt_addon.module = addon.module


@persistent
def adt_load_post_handler(dummy):
    context = bpy.context

    adt_preferences = context.user_preferences.addons['ab_addons_tools'].preferences
    context.window_manager.adt_save = bpy.data.scenes[0].adt_save

    if (adt_preferences.load):
        adt_enable_addons()

   
def register():
    # Apparently need to register does classes before Add-on registers them.
    bpy.utils.register_class(AddonsToolsPreferences)
    bpy.utils.register_class(ADTAddonItem)
    bpy.utils.register_class(ADTEnableAddonsOperator)
    
    bpy.types.INFO_MT_file.prepend(adt_menu_draw)

    adt_preferences = bpy.context.user_preferences.addons[__name__].preferences
    
    # Properties
    bpy.types.Scene.adt_addons = bpy.props.CollectionProperty(type=ADTAddonItem)
    bpy.types.Scene.adt_save = bpy.props.BoolProperty('ADT Save Add-ons', default=True)
    bpy.types.WindowManager.adt_save = bpy.props.BoolProperty('ADT Save Add-ons', default=True, update=adt_save_update)

    bpy.app.handlers.save_pre.append(adt_save_pre_handler);
    bpy.app.handlers.load_post.append(adt_load_post_handler)
    
    
def unregister():
    bpy.utils.unregister_class(AddonsToolsPreferences)
    bpy.utils.unregister_class(ADTAddonItem)
    bpy.utils.unregister_class(ADTEnableAddonsOperator)

    bpy.types.INFO_MT_file.remove(adt_menu_draw)

    bpy.app.handlers.save_pre.remove(adt_save_pre_handler);
    bpy.app.handlers.load_post.remove(adt_load_post_handler)
    
    del bpy.types.Scene.adt_addons
    del bpy.types.Scene.adt_save
    del bpy.types.WindowManager.adt_save
    
