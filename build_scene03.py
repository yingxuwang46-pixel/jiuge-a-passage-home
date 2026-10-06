import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
assets={}
for folder in ['assets','assets03']:
 for p in (ROOT/'build'/folder).glob('*.blend'):
  with bpy.data.libraries.load(str(p)) as (src,dst):dst.objects=[n for n in src.objects]
  assets[p.stem]=[o for o in dst.objects if o.type=='MESH']
def mesh(asset,name,loc,height=None,scale=None):
 src=assets[asset][0];o=src.copy();o.data=src.data;s.collection.objects.link(o);o.name=name
 lo=min(v.co.z for v in o.data.vertices);hi=max(v.co.z for v in o.data.vertices)
 scale=scale or height/(hi-lo);o.scale=(scale,)*3 if isinstance(scale,(float,int)) else scale;o.location=loc;o.location.z-=lo*o.scale.z;return o
ledge=mesh('cliff_ledge_01','Mountain_Ledge',(-7,0,-8),scale=(63,32,30))
bpy.context.view_layer.update()
def ground(x,y):
 origin=ledge.matrix_world.inverted()@Vector((x,y,100));direction=Vector((0,0,-1));hit,p,n,i=ledge.ray_cast(origin,direction)
 return (ledge.matrix_world@p).z if hit else 1
base=ground(-4,-3)
tree=mesh('serpentine_tree_01','Serpentine_Tree',(-6,0,base-.7),height=14)
rider=mesh('rider_leopard_complete_01','Veiled_Rider',(-2,-3,base),height=7)
wall=mesh('cliff_01','Mountain_Wall_Left',(-37,16,-22),height=70);wall.scale.x*=.72
wall=mesh('cliff_02','Mountain_Wall_Back',(-34,46,-25),height=76);wall.scale.x*=.65
for i,(x,y,z,h) in enumerate([(19,53,-28,45),(40,88,-35,74),(9,105,-40,62),(60,125,-35,90),(29,135,-32,65)]):
 o=mesh('peak_0'+str(i%3+1),f'Mountain_Peak_{i}',(x,y,z),height=h);o.rotation_euler.z=i*.7;o.scale.x*=.52;o.scale.y*=.62;o.scale.z*=1.8;o.location.z-=h*.8
bpy.context.view_layer.update()
pts=[rider.matrix_world@v.co for v in rider.data.vertices];top=max(p.z for p in pts);heads=[p for p in pts if p.z>top-.45];head=sum(heads,Vector())/len(heads)
anchors={'Perch_Veil':head+Vector((0,-.15,.1)),'Perch_Branch':Vector((-7,-.8,base+10)),'Perch_Leopard':Vector((1.1,-3.6,base+2.7))}
# Find a real branch surface nearest the desired perch.
tpts=[tree.matrix_world@v.co for v in tree.data.vertices];anchors['Perch_Branch']=min(tpts,key=lambda p:(p-anchors['Perch_Branch']).length)+Vector((0,-.05,.08))
# Leopard head lies at the right edge of the combined asset.
right=max(p.x for p in pts);lp=[p for p in pts if p.x>right-.5];anchors['Perch_Leopard']=max(lp,key=lambda p:p.z)+Vector((0,0,.08))
for name,pos in anchors.items():
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.location=pos
root=bpy.data.objects.new('Butterfly_Template',None);s.collection.objects.link(root)
center=Vector((0,-.02,.34))
for src in assets['orange_butterfly_01']:
 o=src.copy();o.data=src.data;s.collection.objects.link(o)
 cx=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)
 if abs(cx)>.12:
  side='Right' if cx>0 else 'Left';pivot=bpy.data.objects.new('Wing_'+side+'_Pivot',None);s.collection.objects.link(pivot);pivot.parent=root;pivot.location=Vector((.022 if cx>0 else -.022,-.03,.34))-center
  o.parent=pivot;o.location=-Vector((.022 if cx>0 else -.022,-.03,.34));o.name='Wing_'+side
 else:o.parent=root;o.location=-center;o.name='Butterfly_Body'
root.location=(1000,0,0)
for o in list(s.objects):
 if o.type=='MESH' and ('Mountain_' in o.name):
  for m in o.data.materials:
   if m:m['web_color_multiplier']=[.55,.67,.68]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'build/web_handoff/jiuge_mountain.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
# Visible, independently articulated butterflies for the submission project.
for i,(name,pos) in enumerate(anchors.items()):
 mapping={}
 for src in [root]+list(root.children_recursive):
  cp=src.copy();s.collection.objects.link(cp);mapping[src]=cp;cp.name='Preview_'+str(i)+'_'+src.name
 for src,cp in mapping.items():
  if src.parent in mapping:cp.parent=mapping[src.parent]
 r=mapping[root];r.location=pos;r.scale=(.7,)*3
 for src,cp in mapping.items():
  if 'Pivot' in src.name:
   sign=1 if 'Right' in src.name else -1
   for f,a in [(1,.15),(12,.75),(24,.15)]:cp.rotation_euler.z=a*sign;cp.keyframe_insert(data_path='rotation_euler',frame=f)
world=bpy.data.worlds.new('Pale valley sky');world.use_nodes=True;s.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(.53,.67,.7,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='SUN',location=(10,-15,35));o=bpy.context.object;o.data.energy=2;o.data.angle=.3;aim(o,(0,0,0))
bpy.ops.object.light_add(type='AREA',location=(0,-15,23));o=bpy.context.object;o.data.energy=1900;o.data.size=18;aim(o,(-3,0,5))
bpy.ops.mesh.primitive_plane_add(size=800,location=(0,0,-22));o=bpy.context.object;o.name='Valley_Water';m=bpy.data.materials.new('Deep teal water');m.diffuse_color=(.035,.09,.1,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.22;o.data.materials.append(m)
bpy.ops.mesh.primitive_cube_add(size=1,location=(20,85,0));o=bpy.context.object;o.name='Valley_Mist';o.scale=(180,150,110);m=bpy.data.materials.new('Valley mist');m.use_nodes=True;m.node_tree.nodes.clear();v=m.node_tree.nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.009;v.inputs['Color'].default_value=(.65,.76,.8,1);out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume']);o.data.materials.append(m)
bpy.ops.object.camera_add(location=(13,-32,base+12));o=bpy.context.object;o.name='Camera_Mountain';o.data.lens=36;aim(o,(1,0,base+7));s.camera=o
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1440;s.render.resolution_y=740;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for im in bpy.data.images:
 if im.has_data:
  try:im.pack()
  except:pass
s['chapter']='III — Where Memory Takes Wing';s['interaction']='Wake butterfly; choose veil, branch or leopard. Chapter IV connection reserved.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/jiuge_mountain_v01.blend'))
s.render.filepath=str(ROOT/'blender/mountain_scene_preview.png');bpy.ops.render.render(write_still=True)
(ROOT/'build/scene03_report.json').write_text(json.dumps({'base':base,'anchors':{k:list(v) for k,v in anchors.items()}},indent=2))
