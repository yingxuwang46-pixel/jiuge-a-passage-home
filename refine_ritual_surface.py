import bpy,math
from pathlib import Path
root=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(root/'blender/jiuge_ritual_v01.blend'));o=bpy.data.objects['Sun_Phoenix_Banner'];mesh=o.data
attr=mesh.attributes.new('DrumEdgeLight','FLOAT','POINT')
for v,d in zip(mesh.vertices,attr.data):
 x,y,z=v.co;r=math.hypot((x+.0007)/.101,(z-.8681)/.096);front=max(0,min(1,(-y-.046)/.015));front=front*front*(3-2*front);d.value=(math.exp(-((r-.94)/.085)**2)+.22*math.exp(-((r-.91)/.17)**2))*front
for i,old in enumerate(list(mesh.materials)):
 m=old.copy();mesh.materials[i]=m;m.name=old.name+'_SurfaceGold';nodes=m.node_tree.nodes;links=m.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');a=nodes.new('ShaderNodeAttribute');a.attribute_name='DrumEdgeLight';mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';links.new(a.outputs['Fac'],mul.inputs[0]);links.new(mul.outputs[0],bs.inputs['Emission Strength']);bs.inputs['Emission Color'].default_value=(.9,.48,.08,1)
 for f,value in [(1,0),(330,1),(1020,1)]:mul.inputs[1].default_value=value;mul.inputs[1].keyframe_insert(data_path='default_value',frame=f)
s=bpy.context.scene;s.frame_set(1);s['awakening_effect']='Gold emission directly on the drum face edge. No separate halo geometry; original center color preserved.'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/jiuge_ritual_v03.blend'));print('SURFACE_GOLD_SAVED')
