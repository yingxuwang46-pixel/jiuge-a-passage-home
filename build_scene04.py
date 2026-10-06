import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;assets={}
for p in (ROOT/'build/assets04').glob('*.blend'):
 with bpy.data.libraries.load(str(p)) as (src,dst):dst.objects=src.objects
 assets[p.stem]=next(o for o in dst.objects if o.type=='MESH')
def put(asset,name,loc,height=None,scale=None,rot=0):
 src=assets[asset];o=src.copy();o.data=src.data;s.collection.objects.link(o);o.name=name;o.parent=None
 lo=min(v.co.z for v in o.data.vertices);hi=max(v.co.z for v in o.data.vertices);scale=scale or height/(hi-lo)
 o.scale=(scale,)*3 if isinstance(scale,(int,float)) else scale;o.location=loc;o.location.z-=lo*o.scale.z;o.rotation_euler.z=rot;return o
ledge=put('ritual_ledge_01','Ritual_Platform',(-13,0,-5),scale=(33,23,17))
put('cliff_left_01','Ritual_Cliff_Left',(-36,9,-34),height=90)
put('cliff_right_01','Ritual_Cliff_Right',(45,28,-42),height=105,rot=-.15)
put('cliff_right_01','Ritual_Platform_Support',(-18,7,-54),height=55)
for i,(x,y,z,h) in enumerate([(-20,53,-45,78),(12,80,-50,72),(33,100,-48,100),(-10,118,-55,94),(53,135,-55,112),(-45,110,-50,103)]):
 o=put(['peak_pointed_01','peak_rounded_01','peak_broken_01'][i%3],f'Ritual_Peak_{i}',(x,y,z),height=h,rot=i*.41);o.scale.x*=.75;o.scale.y*=.75
bpy.context.view_layer.update()
def ground(x,y):
 ok,p,n,index=ledge.ray_cast(ledge.matrix_world.inverted()@Vector((x,y,100)),Vector((0,0,-1)))
 return (ledge.matrix_world@p).z if ok else 0
people=[]
for i in range(8):
 x=-23+i*2.15;y=-3+math.sin(i*.65)*.4;z=ground(x,y)
 o=put('umbrella_worshipper_01' if i==4 else 'white_worshipper_01',f'Worshipper_{i:02}',(x,y,z),height=4.7 if i==4 else 3.2,rot=1.15);people.append(o)
for i,(x,y) in enumerate([(-26,3),(-28,9),(-22,10)]):put('cliff_tree_01',f'Ritual_Tree_{i}',(x,y,ground(x,y)),height=5+i)
banner=put('sun_phoenix_banner_01','Sun_Phoenix_Banner',(4,10,1),height=31)
bpy.context.view_layer.update()
verts=[banner.matrix_world@v.co for v in banner.data.vertices];low=min(v.z for v in verts);high=max(v.z for v in verts)
anchors={'Sun_Anchor':(4,9,low+(high-low)*.875),'Queue_Target':(-15,-3,sum(o.location.z for o in people)/8+2),'Overview_Target':(-4,5,14)}
for name,loc in anchors.items():o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.location=loc
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(ROOT/'build/web_handoff/jiuge_ritual.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
# Keep the disk and birds rigid; only the lower cloth receives a preview shape key.
banner.shape_key_add(name='Basis');key=banner.shape_key_add(name='Banner_Breeze');lo=min(v.co.z for v in banner.data.vertices);hi=max(v.co.z for v in banner.data.vertices);span=hi-lo
for v,p in zip(banner.data.vertices,key.data):
 t=max(0,min(1,(lo+span*.65-v.co.z)/(span*.65)));p.co.x+=math.sin(t*5)*t*t*.035;p.co.y+=math.sin(t*4+1)*t*t*.015
for f,val in [(1,0),(65,1),(130,0),(195,.8),(260,0)]:key.value=val;key.keyframe_insert(data_path='value',frame=f)
world=bpy.data.worlds.new('Ritual overcast sky');world.use_nodes=True;s.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.65,.7,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='SUN',location=(10,-20,50));o=bpy.context.object;o.data.energy=2.5;o.data.angle=.3;aim(o,(-10,0,0))
bpy.ops.object.light_add(type='AREA',location=(-8,-20,22));o=bpy.context.object;o.data.energy=1900;o.data.size=25;aim(o,(-13,0,2))
bpy.ops.mesh.primitive_cube_add(size=1,location=(10,80,-12));o=bpy.context.object;o.name='Ritual_Valley_Mist';o.scale=(200,155,125);m=bpy.data.materials.new('Ritual patchy mist');m.use_nodes=True;n=m.node_tree.nodes;n.clear();v=n.new('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.55,.67,.7,1);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=3;r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.001;r.inputs['To Max'].default_value=.018;out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(noise.outputs['Fac'],r.inputs['Value']);m.node_tree.links.new(r.outputs['Result'],v.inputs['Density']);m.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume']);o.data.materials.append(m)
bpy.ops.object.camera_add(location=(13,-61,17));cam=bpy.context.object;cam.name='Camera_Ritual';cam.data.lens=32;cam.data.clip_end=1500;aim(cam,(-5,5,14));s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1440;s.render.resolution_y=760;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.frame_end=260
for im in bpy.data.images:
 if im.has_data:
  try:im.pack()
  except:pass
s['chapter']='IV — Beneath the Silent Sun';s['next_chapter']=5
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/jiuge_ritual_v01.blend'));s.render.filepath=str(ROOT/'blender/ritual_scene_preview.png');bpy.ops.render.render(write_still=True)
(ROOT/'build/scene04_report.json').write_text(json.dumps({'anchors':anchors,'people':[list(o.location) for o in people]},indent=2))
