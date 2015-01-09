# ab_groups_particles_tools.py Copyright (C) 2012, Jakub Zolcik
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
    "name": "Groups Particles Tools",
    "author": "Jakub Zolcik",
    "version": (0, 0, 1),
    "blender": (2, 7, 2),
    "location": "View3D -> Tool Shelf",
    "description": "Allows advanced usage of Particles with Object Groups.",
    "warning": "",
    "wiki_url": "https://studio.allblue.pl/wiki/wikis/blender/group-particles-tools/",
    "tracker_url": "https://github.com/sftd/AllBlue-Blender-Tools",
    "category": "Animation"
}

"""
Usage:

To Do.
"""


import bpy
import mathutils
import random


class GPTMatchGroupsLengthsOperator(bpy.types.Operator):
    bl_idname = 'object.gpt_match_groups_lengths'
    bl_label = 'GPT Match Groups Lengths'

    group_name1 = bpy.props.StringProperty(name='Group Name')
    group_name2 = bpy.props.StringProperty(name='Group Name')
    
    remove_doubles = bpy.props.BoolProperty(name='Remove Doubles', default=False)
    
    def execute(self, context):
        if (self.group_name1 == '' or self.group_name2 == ''):
            print('No group selected.')
            return {'CANCELLED'}
        
        group1 = bpy.data.groups[self.group_name1]
        group2 = bpy.data.groups[self.group_name2]
        
        if (len(group1.objects) == 0 or len(group2.objects) == 0):
            printf('Empty group selected.')
            return {'CANCELLED'}
        
        if (len(group2.objects) > len(group1.objects)):
            t_group = group1
            group1 = group2
            group2 = t_group
            
        group2_objects_len = len(group2.objects)
            
        while (len(group1.objects) > group2_objects_len):
            t_group1_objects = group1.objects[:]
            
            while (len(group1.objects) > group2_objects_len and len(t_group1_objects) > 1):
                #print('Objects: ', t_group1_objects)
                
                object_i = random.randint(0, len(t_group1_objects) - 1)
                object1 = t_group1_objects[object_i]
                t_group1_objects.remove(object1)
                
                object2 = self.getClosestObject(group1.objects, object1)
                # print('Found: ', object1, object2)
                if (object2 in t_group1_objects):
                    t_group1_objects.remove(object2)
                
                bpy.ops.object.select_all(action='DESELECT')
                
                context.scene.objects.active = object1
                object1.select = True
                object2.select = True
                
                new_location = (object1.location - object2.location) / 2.0
                
                #print("Objects: ", object1, object2)
                # print('Context:', context.mode)
                bpy.ops.object.join()
                
                context.scene.cursor_location = new_location
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                # object1.location = new_location
                
                if (self.remove_doubles):
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.remove_doubles()
                    bpy.ops.object.mode_set(mode='OBJECT')
        
        #print("Group1: ", len(group1.objects))
        #print("Group2: ", len(group2.objects))
                
        return {'FINISHED'}
    
    def invoke(self, context, event):
        window_manager = context.window_manager
        return window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        column = layout.column()        
        row = column.row()
        row.prop_search(data = self, property = 'group_name1', search_data = bpy.data, search_property = 'groups')
        
        column = layout.column()        
        row = column.row()
        row.prop_search(data = self, property = 'group_name2', search_data = bpy.data, search_property = 'groups')
        
        column = layout.column()
        row = column.row()
        row.prop(data = self, property = 'remove_doubles')

    def getClosestObject(self, objects, object):
        closest_t_object = None
        closest_distance = 3.40282e+038
        
        location = object.location
        for t_object in objects:
            if (object == t_object):
                continue
            
            distance = (location - t_object.location).length
            if (distance < closest_distance):
                closest_t_object = t_object
                closest_distance = distance
                
        return closest_t_object
        
#    def getDistance(self, location1, location2):
#        return (location1[0] - location2[0]) * (location1[0] - location2[0]) + \
#               (location1[1] - location2[1]) * (location1[1] - location2[1]) + \
#               (location1[2] - location2[2]) * (location1[2] - location2[2])
        

class GPTCreateGroupMeshOperator(bpy.types.Operator):
    bl_idname = 'object.gpt_create_group_mesh'
    bl_label = 'GPT Create Group Mesh'
    
    group_name = bpy.props.StringProperty(name='Group Name')
    gm_object_name = bpy.props.StringProperty(name='')
    
    def execute(self, context):
        if (self.group_name == ''):
            raise Exception('No group selected.')
            return {'CANCELLED'}
        
        group = bpy.data.groups[self.group_name]
        
        if (len(group.objects) == 0):
            raise Exception('Empty group selected.')
            return {'CANCELLED'}
        
        # Setup
        bpy.ops.object.select_all(action='DESELECT')
        
        # Create new mesh or remove vertices from existing mesh.
        if (self.gm_object_name == ''):
            gm_mesh = bpy.data.meshes.new(self.group_name + '_Mesh')
            gm_object = bpy.data.objects.new(self.group_name + '_Mesh', gm_mesh)
            
            context.scene.objects.active = gm_object
            gm_object.select = True
            
            context.scene.objects.link(gm_object)
        else:
            gm_object = bpy.data.objects[self.gm_object_name]
            gm_mesh = gm_object.data
            
            context.scene.objects.active = gm_object
            gm_object.select = True
            
            # Remove all vertices.
            for vertex in gm_mesh.vertices:
                vertex.select = True
                
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.delete()
            bpy.ops.object.mode_set(mode='OBJECT')
        
        vertices = []
        
        # Calculate Group Center        
        group_objects_length = len(group.objects)
        group_center = mathutils.Vector((0.0, 0.0, 0.0))
        for i in range(group_objects_length):
            group_center = (i * group_center + group.objects[i].location) / (i + 1)
        
        for object in group.objects:
            vertices.append(object.location - group_center)
        vertices.append(mathutils.Vector((0.0, 0.0, 0.0)))
        
        gm_mesh.from_pydata(vertices, [], [])
        gm_mesh.update()
        
        gm_object.gpt_group_name = group.name
        
        # If  it'a a new Group Mesh set location to Group Center.
        if (self.gm_object_name == ''):
            gm_object.location = group_center
            context.scene.objects.active = gm_object
            gm_object.select = True
        
        group.gpt_mesh_name = gm_object.name
        bpy.ops.object.gpt_update_group(group_name=group.name)
        
        # Clean Up
        bpy.ops.view3d.snap_cursor_to_active()
        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        window_manager = context.window_manager
        return window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        column = layout.column()
        #column.label('Create Vertices Mesh')
        
        row = column.row()
        row.prop_search(data = self, property = 'group_name', search_data = bpy.data, search_property = 'groups')
        
        
class GPTUpdateGroupOperator(bpy.types.Operator):
    bl_idname = 'object.gpt_update_group'
    bl_label = 'GPT Update Group'
    
    group_name = bpy.props.StringProperty(name='Group Name')
    update_vertices = bpy.props.BoolProperty(name='Update Vertices')
    
    def execute(self, context):
        if (self.group_name == ''):
            raise Exception('No group selected')
            return {'CANCELLED'}
        
        group = bpy.data.groups[self.group_name]
        
        if (len(group.objects) == 0):
            raise Exception('Empty group selected.')
            return {'CANCELLED'}
        
        if (group.gpt_mesh_name == ''): 
            raise Exception('Group does not have a Group Mesh.')
            return {'CANCELLED'}
        
        gm_object = bpy.data.objects[group.gpt_mesh_name]
        t_group_objects = group.objects[:]
        t_group_objects_length = len(t_group_objects)
        
        if (t_group_objects_length != len(gm_object.data.vertices) - 1 or self.update_vertices):
            # Update Group Mesh vertices.
            bpy.ops.object.gpt_create_group_mesh(group_name=gm_object.gpt_group_name, gm_object_name=gm_object.name)
        
        # Remove Objects from Group and calculate Group Center.
        group_center = mathutils.Vector((0.0, 0.0, 0.0))
        for i in range(t_group_objects_length):
            t_group_object_i = t_group_objects_length - i - 1
            group_center = (i * group_center + group.objects[t_group_object_i].location) / (i + 1)
            group.objects.unlink(group.objects[t_group_object_i])
        
        # Find Objects closest to Vertex and add it to group.
        for vertex_i in range(t_group_objects_length):
            vertex = gm_object.data.vertices[vertex_i]
                    
            # Move Zero Vertex to the end of a Group Mesh. 
            if (vertex.co.x == 0.0 and vertex.co.y == 0.0 and vertex.co.z == 0.0):
                vertex.co = gm_object.data.vertices[vertex_i + 1].co
                gm_object.data.vertices[vertex_i + 1].co = mathutils.Vector((0.0, 0.0, 0.0))
                
            closest_object = None
            closest_distance = 3.40282e+038
            
            for object in t_group_objects:
                distance = (vertex.co - (object.location - group_center)).length
                if (distance < closest_distance):
                    closest_object = object
                    closest_distance = distance
                    
            t_group_objects.remove(closest_object)
            group.objects.link(closest_object)
            
        return {'FINISHED'}

    def invoke(self, context, event):
        window_manager = context.window_manager
        return window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        column = layout.column()
        #column.label('Create Vertices Mesh')
        
        row = column.row()
        row.prop_search(data = self, property = 'group_name', search_data = bpy.data, search_property = 'groups')


class GPTUpdateAllGroups(bpy.types.Operator):
    bl_idname = 'object.gpt_update_all_groups'
    bl_label = 'GPT Update All Groups'
    
    def execute(self, context):
        for group in bpy.data.groups:
            if (group.gpt_mesh_name != ''):
                bpy.ops.object.gpt_update_group(group_name=group.name)
                
        return {'FINISHED'}
    
    
class GPTSetupGroupParticlesSystem(bpy.types.Operator):
    bl_idname = 'object.gpt_setup_groups_particle_system'
    bl_label = 'GPT Setup Group Mesh Particle System'
    
    def execute(self, context):
        gm_object = context.active_object
        
        if (gm_object.gpt_group_name == ''):
            raise Exception('Object is not a Group Mesh.')
         
        # Update Group Mesh just in case.
        bpy.ops.object.gpt_update_group(group_name=gm_object.gpt_group_name)
         
        group = bpy.data.groups[gm_object.gpt_group_name]
            
        if (len(gm_object.particle_systems) == 0):
            bpy.ops.object.particle_system_add()
            gm_object.particle_systems.active.name = gm_object.gpt_group_name
            gm_object.particle_systems.active.settings.name = gm_object.gpt_group_name
            
        particle_system = gm_object.particle_systems.active
         
        particle_system.settings.count = len(group.objects)
        particle_system.settings.emit_from = 'VERT'
        particle_system.settings.use_emit_random = False
          
        particle_system.settings.use_rotations = True
        particle_system.settings.rotation_mode = 'OB_X'
         
        particle_system.settings.use_rotation_dupli = True
        particle_system.settings.use_scale_dupli = False
        particle_system.settings.particle_size = 1.0
            
        return {'FINISHED'}
    
def register(is_submodule=False):
    # Properties
    bpy.types.Group.gpt_mesh_name = bpy.props.StringProperty()
    bpy.types.Object.gpt_group_name = bpy.props.StringProperty()

    # Module
    if (not is_submodule):
        bpy.utils.register_module(__name__)
    
    
def unregister(is_submodule=False):
    # Module
    if (not is_submodule):
        bpy.utils.unregister_module(__name__)

    # Properties
    del bpy.types.Group.gpt_mesh_name
    del bpy.types.Object.gpt_group_name

    
if __name__ == "__main__":
    register()
