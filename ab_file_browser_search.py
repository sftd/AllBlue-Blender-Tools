# ab_file_brower_search.py Copyright (C) 2012, Jakub Zolcik
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
    "name": "File Browser Search",
    "author": "Jakub Zolcik",
    "version": (0, 1, 2),
    "blender": (2, 7, 2),
    "location": "File Browser",
    "description": "Searches through files in the file browser by name.",
    "warning": "",
    "wiki_url": "https://studio.allblue.pl/wiki/wikis/blender/file-browser-search/",
    "tracker_url": "https://github.com/sftd/AllBlue-Blender-Tools",
    "category": "Import-Export"
}

"""
Usage:

Launches in File Browser
"""

import bpy
import os
import re


# Single search result
class SearchResultsItem(bpy.types.PropertyGroup):

    isBlendData = bpy.props.BoolProperty(name="Is Blend Data")
    isDirectory = bpy.props.BoolProperty(name="Is Directory")
    file = bpy.props.StringProperty(name="File Path",
                                    default="")
    fileName = bpy.props.StringProperty(name="File Name",
                                        default="")
    fileExtension = bpy.props.StringProperty(name="File Extension")


# File Browser Search Select Operator
class FBSFileSelectOperator(bpy.types.Operator):

    bl_idname = "file.fbs_file_select"
    bl_label = "Select File"

    searchBlendData = bpy.props.BoolProperty()
    isBlendData = bpy.props.BoolProperty()
    isDirectory = bpy.props.BoolProperty()
    file = bpy.props.StringProperty()
    autoExecute = bpy.props.BoolProperty()

    def execute(self, context):
        if (self.autoExecute):
            t_file = self.file
            if (self.searchBlendData):
                t_file = os.path.dirname(t_file)

            if (self.isDirectory or 
                    (self.searchBlendData and not self.isBlendData)):
                directory = context.space_data.params.directory
                directory = os.path.join(directory, t_file)
                context.window_manager.fbs_filter = ""
                # Apparentl bpy.ops.file.select_bookmark operators
                # is actually select_directory operator...
                bpy.ops.file.select_bookmark(dir=directory)
            else:
                context.space_data.params.filename = t_file
                bpy.ops.file.execute('INVOKE_DEFAULT')
        else:
            context.space_data.params.filename = self.file

        return {'FINISHED'}


class FBSSearchResultsPanel(bpy.types.Panel):

    # Place panel on the bottom left of the file Browser
    bl_idname = "FILE_PT_fbs_search_results_panel"
    bl_label = "Search:"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'

    # (filter_name, icon_name, [extensions_list])
    EXTENSIONS = (("backup", "FILE_BACKUP", [".blend1", ".blend2"]),
                  ("blender", "FILE_BLEND", [".blend"]),
                  ("font", "FILE_FONT", [".ttf", ".ttc", ".pfb", ".otf",
                                         ".otc"]),
                  ("image", "FILE_IMAGE", [".png", ".tga", ".bmp", ".jpg",
                                           ".jpeg", ".sgi", ".rgb", ".rgba",
                                           ".tif", ".tiff", ".tx", ".jp2",
                                           ".j2c", ".hdr", ".dds", ".dpx",
                                           ".cin", ".exr", ".psd", ".pdd",
                                           ".psb"]),
                  ("movie", "FILE_MOVIE", [".avi", ".flc", ".mov", ".movie",
                                           ".mp4", ".m4v", ".m2v", ".m2t",
                                           ".m2ts", ".mts", ".ts", ".mv",
                                           ".avs", ".wmv", ".ogv", ".ogg",
                                           ".r3d", ".dv", ".mpeg", ".mpg",
                                           ".mpg2", ".vob", ".mkv", ".flv",
                                           ".divx", ".xvid", ".mxf", ".webm"]),
                  ("script", "FILE_SCRIPT", [".py"]),
                  ("sound", "FILE_SOUND", [".wav", ".ogg", ".oga", ".mp3",
                                           ".mp2", ".ac3", ".aac", ".flac",
                                           ".wma", ".eac3", ".aif", ".aiff",
                                           ".m4a", ".mka"]),
                  ("text", "FILE_TEXT", [".txt", ".glsl", ".osl", ".data"]))

    @classmethod
    def poll(cls, context):
        return (context.space_data.params is not None)

    def draw(self, context):
        layout = self.layout

        # Get current directory in the File Browser
        directory = context.space_data.params.directory

        search_blend_data = False
        if (context.active_operator):
            if (context.active_operator.bl_idname == "WM_OT_link_append" or
                context.active_operator.bl_idname == "WM_OT_link" or
                context.active_operator.bl_idname == "WM_OT_append"):
                search_blend_data = True

        # If the search was initialize or directory in File Browser
        # have changed refresh search results
        if context.window_manager.fbs_search_initialized or \
           context.window_manager.fbs_directory != directory:                       
            context.window_manager.fbs_search_initialized = False
            context.window_manager.fbs_directory = directory

            self.initializeSearch(context, search_blend_data)

        search_results = context.window_manager.fbs_search_results
        search_results_length = len(search_results)

        hide_extensions = bpy.data.scenes[0].fbs_hide_extensions
        auto_execute = bpy.data.scenes[0].fbs_open_on_click
        columns_number = bpy.data.scenes[0].fbs_columns_number

        rows_number = int(search_results_length / columns_number)
        rows_left = search_results_length % columns_number 

        layout.prop(data=context.window_manager, property="fbs_filter",
                    text="", icon="VIEWZOOM")
        box = layout.box()                    

        row = box.row()
        column = row.column()
        i = 0
        row_i = 0

        for search_result in search_results:
            display_name = ''
            if (hide_extensions):
                display_name = search_result.fileName
            else:
                display_name = search_result.file

            if (search_result.isDirectory):
                operator = column.operator("file.fbs_file_select",
                                           text=display_name,
                                           emboss=False, icon='FILE_FOLDER')
            else:
                operator_icon = "FILE_BLANK"

                if (search_result.isBlendData):
                    operator_icon = "BLENDER"

                extension = search_result.fileExtension

                for name, icon, extensions in self.EXTENSIONS:
                    if (extension in extensions):
                        operator_icon = icon
                        break
                operator = column.operator("file.fbs_file_select",
                                           text=display_name,
                                           emboss=False,
                                           icon=operator_icon)

            operator.searchBlendData = search_blend_data
            operator.isBlendData = search_result.isBlendData
            operator.isDirectory = search_result.isDirectory
            operator.file = search_result.file
            operator.autoExecute = auto_execute

            i += 1
            if row_i < rows_left:
                if i % (rows_number + 1) == 0:
                    row_i += 1
                    if(i < search_results_length):
                        column = row.column()
            else:
                if (i - row_i) % rows_number == 0:
                    if(i < search_results_length):
                        column = row.column()

        layout.prop(context.window_manager, "fbs_show_options")

        if (context.window_manager.fbs_show_options):
            box = layout.box()
            box.prop(bpy.data.scenes[0], "fbs_open_on_click")
            box.prop(bpy.data.scenes[0], "fbs_search_in_subdirectories")
            box.prop(bpy.data.scenes[0], "fbs_search_for_directories")
            box.prop(bpy.data.scenes[0], "fbs_hide_extensions")
            box.prop(bpy.data.scenes[0], "fbs_columns_number")

    def initializeSearch(self, context, search_blend_data):
        if (search_blend_data):
            self.searchBlendData(context)
        else:
            self.searchFiles(context)

    def searchFiles(self, context):
        # maximum number of files that can be found
        MAX_RESULTS_COUNT = 100
        # maximum number of files to iterate through
        MAX_FILES_COUNT = 10000
        # maximum number of directories to check
        MAX_DIRS_COUNT = 1000

        # get properties from file browser
        # filter
        filter = context.window_manager.fbs_filter
        filter_prog = self.getProgFromFilter(filter)
        # last directory
        directory = context.window_manager.fbs_directory
        directory_length = len(directory)
        # search results
        search_results = context.window_manager.fbs_search_results
        search_results_length = len(search_results)

        # clear search results
        for search_result in search_results:
            search_results.remove(0)

        if (filter == ""):
            return None

        # Take preferences from first scene
        # for consistency.
        scene = bpy.data.scenes[0]

        search_in_subdirectories = scene.fbs_search_in_subdirectories
        search_for_directories = scene.fbs_search_for_directories

        params = context.space_data.params
        extensions = None
        if (params.use_filter):
            extensions = []
            for filter_type, filter_icon, filter_extensions in self.EXTENSIONS:
                if (getattr(params, "use_filter_" + filter_type)):
                    extensions += filter_extensions

        # variables for counting files and dirs
        results_count = 0
        files_count = 0
        dirs_count = 0

        if (search_in_subdirectories):
            for path, dirs, files in os.walk(directory):
                if (search_for_directories):
                    for dir in dirs:
                        if (self.addSearchResult(context, filter_prog,
                                                 directory_length, path,
                                                 dir, True, extensions,
                                                 False)):
                            results_count += 1
                            if (results_count >= MAX_RESULTS_COUNT):
                                break
                        files_count += 1
                        if (files_count >= MAX_FILES_COUNT):
                            break

                for file in files:
                    if (self.addSearchResult(context, filter_prog,
                                             directory_length, path,
                                             file, False, extensions,
                                             False)):
                        results_count += 1
                        if (results_count >= MAX_RESULTS_COUNT):
                            break
                    files_count += 1
                    if (files_count >= MAX_FILES_COUNT):
                        break

                if (results_count >= MAX_RESULTS_COUNT):
                    break

                if (files_count >= MAX_FILES_COUNT):
                    break

                dirs_count += 1
                if (dirs_count > MAX_DIRS_COUNT):
                    break

        else:
            for file in os.listdir(directory):
                is_directory = os.path.isdir(os.path.join(directory, file))
                if (not is_directory or search_for_directories):
                    if (self.addSearchResult(context, filter_prog, 0, '',
                                             file, is_directory, extensions,
                                             False)):
                        results_count += 1
                        if (results_count >= MAX_RESULTS_COUNT):
                            break
                files_count += 1
                if (files_count >= MAX_FILES_COUNT):
                    break

        return

    def searchBlendData(self, context):
        filter = context.window_manager.fbs_filter
        directory = context.window_manager.fbs_directory

        index = directory.find(".blend")
        # If not in .blend file search for files and directories.
        if (index == -1):
            self.searchFiles(context)
            return

        search_results = context.window_manager.fbs_search_results

        for search_result in search_results:
            search_results.remove(0)

        if (filter == ''):
            return

        index += 6

        file = directory[0:index]

        data_name = directory[index + 1:-1]

        if (data_name == ""):
            return

        datas = self.getBlendDataFromFile(file, data_name)

        filter_prog = self.getProgFromFilter(filter)

        for data in datas:
            self.addSearchResult(context, filter_prog, 0, '',
                                            data, False, None, True)

        return    

    def getBlendDataFromFile(self, file, data_name):
        with bpy.data.libraries.load(file) as (data_from, data_to):
            if (data_name == "Action"):
                return data_from.actions
            elif (data_name == "Armature"):
                return data_from.armatures        
            elif (data_name == "Brush"):
                return data_from.brushes
            elif (data_name == "Camera"):
                return data_from.cameras
            elif (data_name == "Curve"):
                return data_from.curves
            elif (data_name == "Font"):
                return data_from.fonts
            elif (data_name == "Group"):
                return data_from.groups
            elif (data_name == "Image"):
                return data_from.images
            elif (data_name == "Lamp"):
                return data_from.lamps
            elif (data_name == "Lattice"):
                return data_from.lattices
            elif (data_name == "Library"):
                return data_from.libraries
            elif (data_name == "FreestyleLineStyle"):
                return data_from.linestyles
            elif (data_name == "Mask"):
                return data_from.masks
            elif (data_name == "Material"):
                return data_from.materials
            elif (data_name == "Mesh"):
                return data_from.meshes
            elif (data_name == "NodeTree"):
                return data_from.node_groups
            elif (data_name == "Object"):
                return data_from.objects
            elif (data_name == "Particle"):
                return data_from.particles
            elif (data_name == "Scene"):
                return data_from.scenes
            elif (data_name == "Screen"):
                return data_from.screens
            elif (data_name == "Script"):
                return data_from.scripts
            elif (data_name == "Sound"):
                return data_from.sounds
            elif (data_name == "Speaker"):
                return data_from.speakers
            elif (data_name == "Text"):
                return data_from.texts
            elif (data_name == "Texture"):
                return data_from.textures
            elif (data_name == "World"):
                return data_from.worlds
            else:
                return None

    def getProgFromFilter(self, search_filter):
        # setup regular expression pattern
        pattern = ''
        special_characters = ('\\', '.', '^', '$', '*', '+', '?', '{',
                              '}', '[', ']', '|', '(', ')')
        # replace all special characters in search_filter
        for c in special_characters:
            search_filter = search_filter.replace(c, '\\'+c)
        # create regular expression based on search_filter
        if ('*' in search_filter):
            search_filter = search_filter.replace('\*', '.*')
            pattern = ('^' + search_filter.lower() + '$')
        else:
            if(len(search_filter) < 3):
                pattern = ('^' + search_filter.lower() + r".*" + '$')
            else:
                pattern = ('^' + r".*" + search_filter.lower() + r".*" + '$')

        return re.compile(pattern)

    def addSearchResult(self, context, prog, directory_length,
                        path, file, is_directory, extensions,
                        is_blend_data):
        file = (os.path.join(path, file))[directory_length:]

        if (prog.match(file.lower()) is None):
            return False

        file_array = os.path.splitext(file)

        extension = ""
        if (not is_directory):
            extension = file_array[1]
            extension = extension.lower()
            if (extensions is not None):
                if (extension not in extensions):
                    return False

        search_result = context.window_manager.fbs_search_results.add()
        search_result.isBlendData = is_blend_data
        search_result.isDirectory = is_directory
        search_result.file = file
        search_result.fileExtension = extension
        search_result.fileName = file_array[0]

        return True


# Update function for search property
def fbs_initialize_search(self, context):
    context.window_manager.fbs_search_initialized = True


def register():
    bpy.utils.register_module(__name__)

    p = bpy.props

    # global properties set in Scene type
    S = bpy.types.Scene

    S.fbs_open_on_click = p.BoolProperty(name="Open On Click",
                                         default=True)

    prop = p.BoolProperty(name="Search in Subdirectories",
                          update=fbs_initialize_search,
                          default = False)
    S.fbs_search_in_subdirectories = prop

    prop = p.BoolProperty(name="Search for Directories",
                          update=fbs_initialize_search,
                          default=True)
    S.fbs_search_for_directories = prop

    S.fbs_hide_extensions = p.BoolProperty(name="Hide Extensions",
                                           default=False)
    S.fbs_columns_number = p.IntProperty(name="Number of Columns",
                                         default=1, min=1, max=5)

    # temporary properties
    WM = bpy.types.WindowManager 
    WM.fbs_filter = p.StringProperty(update=fbs_initialize_search)
    WM.fbs_search_initialized = p.BoolProperty(default=False)
    WM.fbs_directory = p.StringProperty()
    WM.fbs_search_results = p.CollectionProperty(type=SearchResultsItem)

    WM.fbs_show_options = p.BoolProperty(name="Show Options", default=False)


def unregister():
    del bpy.types.Scene.fbs_open_on_click
    del bpy.types.Scene.fbs_search_in_subdirectories
    del bpy.types.Scene.fbs_hide_extensions
    del bpy.types.Scene.fbs_columns_number

    del bpy.types.WindowManager.fbs_filter
    del bpy.types.WindowManager.fbs_search_initialized
    del bpy.types.WindowManager.fbs_directory
    del bpy.types.WindowManager.fbs_search_results

    del bpy.types.WindowManager.fbs_show_options

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
