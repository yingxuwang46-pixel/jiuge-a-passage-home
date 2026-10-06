import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
groups={}
for name in ['02_Shrine','02_Landscape','02_Hands','02_Atmosphere']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);groups[name]=c
assets={}
for folder in ['assets','assets02']:
 for p in (ROOT/'build'/folder).glob('*.blend'):
  with bpy.data.libraries.load(str(p)) as (src,dst):dst.objects=src.objects
  assets[p.stem]=next(o for o in dst.objects if o.type=='MESH')
def instance(asset,name,loc,height=None,scale=None,rz=0,group='02_Landscape'):
 o=assets[asset].copy();o.data=assets[asset].data;groups[group].objects.link(o);o.name=name
 low=min(v.co.z for v in o.data.vertices);hi=max(v.co.z for v in o.data.vertices)
 if scale is None:scale=height/(hi-low)
 o.scale=(scale,)*3 if isinstance(scale,(int,float)) else scale
 o.rotation_mode='XYZ';o.rotation_euler.z=math.radians(rz);o.location=loc;o.location.z-=low*o.scale.z
 return o
tree=instance('white_tree_01','Remembrance_Tree',(-5,-3,1.4),height=14.5,rz=-5,group='02_Shrine')
keeper=instance('red_robed_figure_01','Keeper',(1.4,-1.2,1.65),height=6.2,rz=12,group='02_Shrine')
instance('cave_cliff_01','Shrine_Cave',(0,6,-1.4),height=17)
instance('sloping_rock_01','Ritual_Ledge',(-4,-3,-1.8),scale=(26,23,8),rz=-12)
for i,(x,y,z,scale,rot) in enumerate([(-15,-3,-1.5,14,32),(-4,-10,-1.8,12,10),(8,-3,-2,12,80),(12,12,-2,16,18)]):
 instance('shore_rock_01',f'Shore02_{i}',(x,y,z),scale=(scale,scale,7),rz=rot)
for i,(x,y,h) in enumerate([(-24,12,46),(-26,43,58)]):
 instance('cliff_01' if i%2==0 else 'cliff_02',f'Cliff02_{i}',(x,y,-5),height=h,rz=i*48)
for i,(x,y,h) in enumerate([(27,60,46),(45,94,68),(15,100,42),(62,135,73),(-8,140,58)]):
 instance('peak_0'+str(i%3+1),f'Peak02_{i}',(x,y,-5),height=h,rz=i*31)
# Templates are hidden at runtime; keep their geometry independent of the tree.
for i in [1,2]:instance(f'hanging_hand_0{i}',f'Hand_Template_{i}',(100+i*3,0,0),height=1,group='02_Hands')
bpy.context.view_layer.update()
random.seed(18)
points=[tree.matrix_world@v.co for v in tree.data.vertices if (tree.matrix_world@v.co).z>8.4]
random.shuffle(points);selected=[]
for p in points:
 if all(math.hypot(p.x-q.x,(p.z-q.z)*1.1)>.8 for q in selected):selected.append(p)
 if len(selected)==54:break
# Anchor points lie on the actual branch surface, not an invented canopy volume.
for i,p in enumerate(selected):
 o=bpy.data.objects.new(f'Branch_Anchor_{i:02}',None);groups['02_Hands'].objects.link(o);o.location=p
 o['hand_variant']=i%2+1
for name,loc in [('Pickup_Anchor',(2.6,-8,2.5)),('Keeper_Offer_Anchor',(1.4,-3.4,5.0))]:
 o=bpy.data.objects.new(name,None);groups['02_Hands'].objects.link(o);o.location=loc
for obj in groups['02_Landscape'].objects:
 for m in obj.data.materials:
  if m:m['web_color_multiplier']=[.5,.61,.63]
# Export only editable world geometry and named interaction anchors.
out=ROOT/'build/web_handoff';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for c in ['02_Shrine','02_Landscape','02_Hands']:
 for o in groups[c].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'jiuge_keeper.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
# Blender preview lighting and water are kept in the editable project.
world=bpy.data.worlds.new('Mist light');world.use_nodes=True;s.world=world
world.node_tree.nodes['Background'].inputs[0].default_value=(.54,.67,.70,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(2,-8,24));light=bpy.context.object;light.data.energy=2300;light.data.size=22;aim(light,(-2,2,4))
bpy.ops.object.light_add(type='SUN',location=(20,-15,40));light=bpy.context.object;light.data.energy=2;light.data.angle=.3;aim(light,(0,0,0))
bpy.ops.mesh.primitive_plane_add(size=600);water=bpy.context.object;water.name='Water02'
m=bpy.data.materials.new('Still teal water');m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.035,.08,.09,1);bs.inputs['Roughness'].default_value=.18;bs.inputs['Metallic'].default_value=.45;water.data.materials.append(m)
bpy.ops.object.camera_add(location=(11,-35,10));cam=bpy.context.object;cam.name='Camera_Keeper';cam.data.lens=34;cam.data.clip_end=1000;aim(cam,(3,1,7));s.camera=cam
for scr in bpy.data.screens:
 for area in scr.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=700;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.render.filepath=str(ROOT/'blender/keeper_scene_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/jiuge_keeper_v01.blend'))
bpy.ops.render.render(write_still=True)
(ROOT/'build/scene02_report.json').write_text(json.dumps({'anchors':len(selected),'objects':len(s.objects),'file':'jiuge_keeper_v01.blend'},indent=2))
print('SCENE02_COMPLETE',len(selected),flush=True)
