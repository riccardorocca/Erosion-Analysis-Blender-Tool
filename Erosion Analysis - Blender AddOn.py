# EROSION ANALYSYS - BLENDER ADDON
# Calculates the amount of erosion of a 3D model from its ideal original geometry.
# Copyright (C) 2025
# Author: Riccardo Rocca <riccardo.rocca@hotmail.com>
# Repository: https://github.com/riccardorocca/Erosion-Analysis-Blender-Tool/

# This add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "Erosion Analysis",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Analysis Tool",
    "author": "Riccardo Rocca <riccardo.rocca@hotmail.com>",
    "location": "3D Viewport > Sidebar > Erosion Analysis",
    "description": "Calculates the erosion distribution of an object over its theoretical original surface",
    "category": "Development",
}

import bpy, os

class SaveDataOperator(bpy.types.Operator):
    """Save input data and selected objects to a file"""
    bl_idname = "object.run_analysis"
    bl_label = "Run Analysis"

    def execute(self, context):
        props = context.scene.my_tool
        erosion_limit = props.erosion_limit
        Zmin = props.Zmin
        Zmax = props.Zmax
        original_obj = props.original_obj
        eroded_obj = props.eroded_obj
        outfilepath = bpy.path.abspath(props.outfile)

        if not original_obj or not eroded_obj:
            self.report({'ERROR'}, "Select two objects with the eyedropper")
            return {'CANCELLED'}

        if not outfilepath:
            self.report({'ERROR'}, "Select a file path using the file browser")
            return {'CANCELLED'}

        if not outfilepath.lower().endswith(".csv"):
            self.report({'ERROR'}, "File must have a .csv extension")
            return {'CANCELLED'}

        try:
            # preliminary setups
            original_mw = original_obj.matrix_world
            eroded_mw = eroded_obj.matrix_world
            eroded_mwi = eroded_mw.inverted()
            matrice = eroded_mwi @ original_mw

            erosion_attribute = "Erosion" #Name of the Color Attribute to store erosion values
            erosions = [] #list of faces with calculated erosions
            transparents = [] #list of faces without calculated erosions and therefore transparent
            f = open(outfilepath, "w")
            f.write("FaceID, X, Y, Z, Area, Erosion, Volume\n")

            #loop through all faces in original_obj
            for face in original_obj.data.polygons:
                [Xc, Yc, Zc] = original_mw @ face.center
                if Zc >= Zmin and Zc <= Zmax:
                    #calculate erosions
                    o = matrice @ face.center                         #vector origin at face center
                    n = matrice @ (face.center + face.normal) - o     #vector orientation normal to face center
                    hit, loc, norm, index = eroded_obj.ray_cast(o, n, distance=erosion_limit) #function ray_cast: returns hit (boolean) and loc (point of hit)

                    #saves the result in the "erosions" list if erosion is within "erosion_limit" and Z is within Zmin-Zmax
                    #otherwise append in the "transparents" list
                    if hit:
                        erosion = (eroded_mw @ o - eroded_mw @ loc).length
                        erosions.append((face.index, erosion))
                        volume = erosion * face.area
                        f.write("%d, %.5e, %.5e, %.5e, %.5e, %.5e, %.5e\n" % (face.index, Xc, Yc, Zc, face.area, erosion, volume))
                    else:
                        transparents.append((face.index))
            f.close()

            #calculate min, max and range of the calculated erosion values
            erosion_data = [row[1] for row in erosions]
            erosion_min = min(erosion_data)
            erosion_max = max(erosion_data)
            erosion_range = erosion_max - erosion_min

            #calculate 99 percentile of erosions
            size = len(erosion_data)
            erosion_p99 = sorted(erosion_data)[int(size * 0.99)]
            props.status_label = "%.3f - %.3f" % (erosion_p99, erosion_max)

            #set a new color attribute
            if not original_obj.data.vertex_colors.get(erosion_attribute):
                original_obj.data.vertex_colors.new(name=erosion_attribute)
            color_layer = original_obj.data.vertex_colors[erosion_attribute]

            #scroll through the list of faces with calculated erosions, and set a corresponding gray color value in the range 0...1
            colors = []
            for face_index, erosion in erosions:
                face = original_obj.data.polygons[face_index]
                for i in face.loop_indices:
                    color = ((erosion - erosion_min) / erosion_range)
                    colors.append((color))
                    color_layer.data[i].color = (color,color,color,1)

            #scroll through the list of faces without calculated erosions, and set them transparent
            for face_index in transparents:
                face = original_obj.data.polygons[face_index]
                for i in face.loop_indices:
                    color_layer.data[i].color = (0,0,0,0)

            # Assign color to original-obj based on selection
            if 'ErosionMaterial' in bpy.data.materials:
                material = bpy.data.materials['ErosionMaterial']
                bpy.data.materials.remove(material)

            #create a new material with grey shades or rainbow colors
            material = bpy.data.materials.new(name="ErosionMaterial")
            node_tree = material.node_tree
            material.use_nodes = True
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            nodes.clear()
            material.blend_method = 'BLEND'
            material.show_transparent_back = False

            attribute_node = nodes.new(type='ShaderNodeVertexColor')
            attribute_node.layer_name = "Erosion"
            attribute_node.location = (0, 310)

            RGBToBW_node = nodes.new(type='ShaderNodeRGBToBW')
            RGBToBW_node.location = (200, 360)

            math_node = nodes.new(type='ShaderNodeMath')
            math_node.operation = "POWER"
            math_node.location = (400, 430)

            ValToRGB_node = nodes.new(type='ShaderNodeValToRGB')
            ValToRGB_node.width = 700
            ValToRGB_node.location = (600,480)

            principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            principled_node.location = (1350, 400)

            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (1650, 400)

            links.new(attribute_node.outputs[0], RGBToBW_node.inputs[0])
            links.new(attribute_node.outputs[1], principled_node.inputs[4])
            links.new(RGBToBW_node.outputs[0], math_node.inputs[0])
            links.new(math_node.outputs[0], ValToRGB_node.inputs[0])
            links.new(ValToRGB_node.outputs[0], principled_node.inputs[0])
            links.new(principled_node.outputs[0], output_node.inputs[0])

            if props.original_obj_color == 'GREYS':
                math_node.inputs[1].default_value = 1
                ValToRGB_node.color_ramp.color_mode = 'RGB'
                ValToRGB_node.color_ramp.interpolation = 'LINEAR'
                ValToRGB_node.color_ramp.elements[0].color = (0, 0, 0, 1)
                ValToRGB_node.color_ramp.elements[1].color = (1, 1, 1, 1)
            else:
                math_node.inputs[1].default_value = 0.455
                ValToRGB_node.color_ramp.color_mode = 'HSV'
                ValToRGB_node.color_ramp.hue_interpolation = 'CCW'
                ValToRGB_node.color_ramp.elements[0].color = (0, 0, 1, 1)
                ValToRGB_node.color_ramp.elements[1].color = (1, 0, 0, 1)

            # Assign material to original_obj
            if original_obj.data.materials:
                # assign to 1st material slot
                original_obj.data.materials[0] = material
            else:
                # no slots
                original_obj.data.materials.append(material)

            #opens a new Shader Editor if it does not already exist
            node_editor = False
            for area in bpy.context.screen.areas:
                if area.type == "NODE_EDITOR":
                    node_editor = True
            if not node_editor:
                    bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.3)
                    area = bpy.context.screen.areas[-1]
                    area.type = "NODE_EDITOR"
                    area.ui_type = "ShaderNodeTree"
                    area.spaces[0].show_region_ui = False  #collapse the right toolbar

            #selects and make active original_obj only
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = original_obj
            original_obj.select_set(True)

            #sets the viewport Shading to MATERIAL
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'
                            break

            self.report({'INFO'},"Erosion Analysis executed")

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

class ResetPropertiesOperator(bpy.types.Operator):
    """Reset all input fields to default values"""
    bl_idname = "object.reset_properties"
    bl_label = "Reset Parameters"

    def execute(self, context):
        props = context.scene.my_tool
        props.erosion_limit = 1.0
        props.Zmin = 0.0
        props.Zmax = 10.0
        props.outfile = ""
        props.original_obj = None
        props.eroded_obj = None
        props.original_obj_color = 'GREYS'
        props.status_label = ""
        self.report({'INFO'}, "All parameters reset")
        return {'FINISHED'}

class MyToolPanel(bpy.types.Panel):
    """Creates a Panel in the N-Panel"""
    bl_label = "Erosion Analysis"
    bl_idname = "VIEW3D_PT_ErosionAnalysis"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Erosion Analysis'

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_tool

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.operator("object.reset_properties")
        layout.prop(props, "original_obj")
        layout.prop(props, "eroded_obj")
        layout.prop(props, "erosion_limit")
        layout.prop(props, "Zmin")
        layout.prop(props, "Zmax")
        layout.prop(props, "original_obj_color", text="Erosion Colors")
        layout.prop(props, "outfile")
        layout.operator("object.run_analysis")
        layout.prop(props, "status_label", text="Erosion p99-pMax")

class MyProperties(bpy.types.PropertyGroup):
    original_obj: bpy.props.PointerProperty(name="Original Object", type=bpy.types.Object)
    eroded_obj: bpy.props.PointerProperty(name="Eroded Object", type=bpy.types.Object)
    erosion_limit: bpy.props.FloatProperty(name="Erosion Limit", default=1.0)
    Zmin: bpy.props.FloatProperty(name="Z Minimum", default=0.0)
    Zmax: bpy.props.FloatProperty(name="Z Maximum", default=10.0)
    outfile: bpy.props.StringProperty(name="File Name (.csv)", subtype='FILE_PATH')
    original_obj_color: bpy.props.EnumProperty(
        name="Erosion Colors",
        description="Choose a color for Original Surface",
        items=[('GREYS', "Grey Scale", "Set object colors to greys"),
               ('RAINBOW', "Rainbow Scale", "Set object colors to rainbow")],
        default='GREYS'
    )
    status_label: bpy.props.StringProperty(name="Status Label", default="")

classes = [SaveDataOperator, ResetPropertiesOperator, MyToolPanel, MyProperties]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
