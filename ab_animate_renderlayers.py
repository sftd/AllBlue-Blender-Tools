# ab_animate_renderlayers.py Copyright (C) 2012, Jakub Zolcik
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
    "name": "Animate Render Layers",
    "author": "Jakub Zolcik",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "Properties -> Render Layers",
    "description": "Allows animating Render Layers visibility.",
    "warning": "",
    "wiki_url": "https://studio.allblue.pl/wiki/wikis/animate-render-layers",
    "tracker_url": "https://github.com/sftd/AllBlue-Blender-Tools",
    "category": "Animation"
}


import bpy
from bpy.app.handlers import persistent


class ARLLayerItem(bpy.types.PropertyGroup):
    visible = bpy.props.BoolProperty("Layer", default=False)


def RENDERLAYER_PT_render_layers_tools_draw(self, context):
    LAYERS_LENGTH = 20
    
    layout = self.layout
    
    column = layout.column()
    
    row = column.row()
    row.prop(context.scene, 'arl_animate_layers', text="Animate Render Layers")

    # Add layers if not there already.
    while (len(context.scene.arl_layers) < LAYERS_LENGTH):
        layer = context.scene.arl_layers.add()
    
    row = layout.row()
    row.alignment = 'CENTER'
    layers_layout = row.column().row()
    for i in range(2):
        layers_column = layers_layout.column(align=True)
        for j in range(2):
            layers_column_row = layers_column.row(align=True)
            for k in range(int(LAYERS_LENGTH / 4)):
                layer_i = int(i * LAYERS_LENGTH / 4) + int(j * LAYERS_LENGTH / 2) + k
                if (context.scene.arl_layers[layer_i].visible):
                    layers_column_row.prop(context.scene.arl_layers[layer_i], \
                                           'visible', toggle=True, text="", expand=True,
                                           icon='VISIBLE_IPO_ON')
                else:
                    layers_column_row.prop(context.scene.arl_layers[layer_i], \
                                           'visible', toggle=True, text="", expand=True,
                                           icon='VISIBLE_IPO_OFF')

@persistent
def arl_frame_change_pre_handler(dummy):
    LAYERS_LENGTH = 20
    scene = bpy.context.scene
    
    # Add layers if not there already.
    while (len(scene.arl_layers) < LAYERS_LENGTH):
        layer = scene.arl_layers.add()
    
    if (not bpy.context.scene.arl_animate_layers):
        return

    for i in range(LAYERS_LENGTH):
        scene.layers[i] = scene.arl_layers[i].visible

   
def register():
    bpy.utils.register_class(ARLLayerItem)

    bpy.types.Scene.arl_animate_layers = bpy.props.BoolProperty("Animate Render Layers", default=False)
    bpy.types.Scene.arl_layers = bpy.props.CollectionProperty(type=ARLLayerItem)
    
    bpy.types.RENDERLAYER_PT_layers.append(RENDERLAYER_PT_render_layers_tools_draw)

    bpy.app.handlers.frame_change_post.append(arl_frame_change_pre_handler)
    
    
def unregister():
    bpy.utils.unregister_class(ARLLayerItem)

    del bpy.types.Scene.arl_animate_layers
    del bpy.types.Scene.arl_layers
    
    bpy.types.RENDERLAYER_PT_layers.remove(RENDERLAYER_PT_render_layers_tools_draw)

    bpy.app.handlers.frame_change_post.remove(arl_frame_change_pre_handler)

