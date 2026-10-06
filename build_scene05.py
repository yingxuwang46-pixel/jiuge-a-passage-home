import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;assets={}
for p in (ROOT/'build/assets05').glob('*.blend'):
 with bpy.data.libraries.load(str(p)) as (src,dst):dst.objects=src.objects
 assets[p.stem]=next(o for o in dst.objects if o.type=='MESH')
def put(asset,name,loc,height=None,scale=None,rot=0):
 src=assets[asset];o=src.copy();o.data=src.data;s.collection.objects.link(o);o.name=name;o.parent=None;lo=min(v.co.z for v in o.data.vertices);hi=max(v.co.z for v in o.data.vertices);scale=scale or height/(hi-lo);o.scale=(scale,)*3 if isinstance(scale,(float,int)) else scale;o.location=loc;o.location.z-=lo*o.scale.z;o.rotation_euler.z=rot;return o
rig=bpy.data.objects.new('Final_Boat_Rig',None);s.collection.objects.link(rig);rig.location=(0,4,0)
o=put('bird_boat_01','Final_Bird_Boat',(0,0,-.35),scale=7.5,rot=math.radians(-40));o.parent=rig
robe=put('empty_white_robe_01','Final_Empty_Robe',(.25,0,.7),height=2.05);robe.parent=rig
bloom=bpy.data.objects.new('Umbrella_Bloom',None);s.collection.objects.link(bloom);bloom.parent=rig;bloom.location=(.25,0,1.65)
um=put('red_petal_umbrella_01','Petal_Umbrella',(0,0,0),height=2.8,rot=-.15);um.parent=bloom
for i,(asset,x,y,z,h,rot) in enumerate([('cliff_left_01',-37,16,-4,76,.1),('cliff_left_01',-49,62,-5,103,.7),('cliff_right_01',47,25,-5,90,-.3),('cliff_right_01',64,88,-6,125,.4)]):
 o=put(asset,f'Final_Cliff_{i}',(x,y,z),height=h,rot=rot)
 if 'right' in asset:o.scale.x*=.72
for i,(x,y,h,asset) in enumerate([(-13,85,69,'peak_column_01'),(22,112,86,'peak_needle_01'),(-36,141,115,'peak_broad_01'),(48,177,136,'peak_column_01'),(6,215,142,'peak_needle_01'),(-8,295,184,'peak_broad_01')]):
 o=put(asset,f'Final_Peak_{i}',(x,y,-5),height=h*.68,rot=i*.45);o.scale.x*=.68;o.scale.y*=.68
# A small sculpted five-petal flower, shared by water instances and interactive blooms.
verts=[];faces=[]
for k in range(5):
 base=len(verts)
 for j in range(10):
  v=j/9
  for i in range(9):
   u=i/8;angle=k*math.tau/5+(u-.5)*math.sin(math.pi*v)*1.25;r=.035+.54*v;z=.025+math.sin(math.pi*v)*.055+v*v*.12+(u-.5)**2*.10
   verts.append((math.cos(angle)*r,math.sin(angle)*r,z))
 for j in range(9):
  for i in range(8):a=base+j*9+i;faces.append((a,a+1,a+10,a+9))
mesh=bpy.data.meshes.new('Red water petals');mesh.from_pydata(verts,[],faces);mesh.update();flower=bpy.data.objects.new('Flower_Template',mesh);s.collection.objects.link(flower);flower.location=(1000,0,0)
m=bpy.data.materials.new('Muted crimson petals');m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.31,.018,.028,1);bs.inputs['Roughness'].default_value=.46;bs.inputs['Subsurface Weight'].default_value=.08;mesh.materials.append(m)
for f in mesh.polygons:f.use_smooth=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(ROOT/'build/web_handoff/jiuge_finale.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
# Animation-ready submission copy: initial empty robe, then blossoming canopy.
for f,sc in [(1,(.001,.001,.001)),(90,(.001,.001,.001)),(125,(.09,.09,.78)),(180,(1,1,1)),(270,(1,1,1))]:bloom.scale=sc;bloom.keyframe_insert(data_path='scale',frame=f)
random.seed(7)
for i in range(65):
 o=flower.copy();o.data=mesh;s.collection.objects.link(o);o.name=f'Water_Flower_{i:02}';o.location=(random.uniform(-24,24),random.uniform(-20,45),.015);size=random.uniform(.18,.5);o.scale=(size,)*3;o.rotation_euler.z=random.random()*math.tau
world=bpy.data.worlds.new('Final pale sky');world.use_nodes=True;s.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(.50,.65,.69,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='SUN',location=(15,-20,60));o=bpy.context.object;o.data.energy=2.3;o.data.angle=.22;aim(o,(0,20,0))
bpy.ops.object.light_add(type='AREA',location=(0,-12,22));o=bpy.context.object;o.data.energy=1300;o.data.size=20;aim(o,(0,4,1))
bpy.ops.mesh.primitive_plane_add(size=1800);water=bpy.context.object;water.name='Final_Water';m=bpy.data.materials.new('Reflective mourning river');m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.035,.075,.082,1);bs.inputs['Metallic'].default_value=.65;bs.inputs['Roughness'].default_value=.19;noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.035;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal']);water.data.materials.append(m)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,130,30));o=bpy.context.object;o.name='Final_Layered_Mist';o.scale=(230,230,120);m=bpy.data.materials.new('Final drifting mist');m.use_nodes=True;n=m.node_tree.nodes;n.clear();v=n.new('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.56,.68,.7,1);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.001;r.inputs['To Max'].default_value=.012;out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(noise.outputs['Fac'],r.inputs['Value']);m.node_tree.links.new(r.outputs['Result'],v.inputs['Density']);m.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume']);o.data.materials.append(m)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Camera_Final_Blossoming';cam.data.lens=32;cam.data.clip_end=2000;s.camera=cam
for f,pos,target in [(1,(10,-36,7),(0,8,8)),(90,(4,-27,5),(0,4,3)),(180,(-5,-29,5),(0,4,3)),(270,(-2,-40,6),(0,12,9))]:cam.location=pos;aim(cam,target);cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
s.frame_end=270;s.render.fps=30;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1440;s.render.resolution_y=740;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for im in bpy.data.images:
 if im.has_data:
  try:im.pack()
  except:pass
s['chapter']='V — A Bloom for the Absent';s['interaction']='Three different flowers; ripples; a petal canopy grows from the empty robe. Boat remains.';s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/jiuge_finale_v01.blend'));s.frame_set(270);s.render.filepath=str(ROOT/'blender/finale_scene_preview.png');bpy.ops.render.render(write_still=True)
print('FINAL_SCENE_SAVED')
