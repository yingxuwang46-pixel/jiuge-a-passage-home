import bpy,math,random
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'blender/jiuge_mountain_v01.blend'))
s=bpy.context.scene
peak=bpy.data.objects.get('Mountain_Peak_0');peak.scale.x*=1.45
bpy.context.view_layer.update()
# Patchy volume density: editable noise-driven mist instead of a uniform white volume.
m=bpy.data.materials.get('Valley mist');n=m.node_tree.nodes;links=m.node_tree.links;v=next(x for x in n if x.type=='PRINCIPLED_VOLUME');v.inputs['Color'].default_value=(.48,.61,.65,1)
t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=3.8;t.inputs['Detail'].default_value=3.2;t.inputs['Roughness'].default_value=.65
mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1.1,1,3.8);coord=n.new('ShaderNodeTexCoord');links.new(coord.outputs['Generated'],mapping.inputs[0]);links.new(mapping.outputs['Vector'],t.inputs['Vector'])
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.28;r.color_ramp.elements[0].color=(.001,.001,.001,1);r.color_ramp.elements[1].position=.76;r.color_ramp.elements[1].color=(.022,.022,.022,1);links.new(t.outputs['Fac'],r.inputs[0]);links.new(r.outputs['Color'],v.inputs['Density'])
random.seed(31);points=[]
for o in list(s.objects):
 if o.type!='MESH' or not o.name.startswith(('Mountain_Peak','Mountain_Wall')):continue
 top=max((o.matrix_world@x.co).z for x in o.data.vertices)
 normalmatrix=o.matrix_world.to_3x3().inverted().transposed()
 for vert in list(o.data.vertices)[::max(1,len(o.data.vertices)//2200)]:
  p=o.matrix_world@vert.co;normal=(normalmatrix@vert.normal).normalized()
  if normal.z>.38 and p.z>max(-4,top-40) and random.random()>.38 and all((p-q).length>.7 for q in points):points.append(p)
  if len(points)>=850:break
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);proto=bpy.context.object;proto.name='Cliff_Scrub_000';mat=bpy.data.materials.new('Weathered mountain scrub');mat.diffuse_color=(.035,.065,.045,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=mat.diffuse_color;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=1;proto.data.materials.append(mat)
collection=bpy.data.collections.new('03_Cliff_Vegetation');s.collection.children.link(collection)
for i,p in enumerate(points):
 o=proto.copy();o.data=proto.data;collection.objects.link(o);o.name=f'Cliff_Scrub_{i+1:03}';radius=random.uniform(.14,.38);o.location=p+Vector((0,0,radius*.3));o.scale=(radius*1.3,radius,radius*.65);o.rotation_euler.z=random.random()*6.28
bpy.data.objects.remove(proto,do_unlink=True)
s['atmosphere_revision']='Noise-driven patchy valley mist; sparse scrub on upward facing mountain shelves. Web equivalent in mountain-atmosphere.js.'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/jiuge_mountain_v02.blend'))
print('REFINED',len(points),'vegetation clumps')
