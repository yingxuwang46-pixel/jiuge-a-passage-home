import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'source-assets/assets05'
CACHE=ROOT/'build/assets05';PREVIEW=ROOT/'build/previews05';CACHE.mkdir(parents=True,exist_ok=True);PREVIEW.mkdir(parents=True,exist_ok=True)
report=[]
for file in sorted(SOURCE.glob('*.glb')):
 name=file.stem.replace(' (1)','')
 if (CACHE/(name+'.blend')).exists():continue
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(file))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in meshes:
  mat=o.matrix_world.copy();o.parent=None;o.matrix_world=mat
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 if 'butterfly' not in name and len(meshes)>1:bpy.ops.object.join();meshes=[bpy.context.object]
 parts=[]
 for i,o in enumerate(meshes):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  o.name=f'Butterfly_Part_{i:02}' if 'butterfly' in name else name
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  before=len(o.data.polygons);target=55000 if 'umbrella' in name else 35000 if 'robe' in name or 'boat' in name else 45000
  if before>target:
   m=o.modifiers.new('Web working copy','DECIMATE');m.ratio=target/before;bpy.ops.object.modifier_apply(modifier=m.name)
  for f in o.data.polygons:f.use_smooth=True
  coords=[v.co for v in o.data.vertices];parts.append({'name':o.name,'triangles':len(o.data.polygons),'min':[min(v[j] for v in coords) for j in range(3)],'max':[max(v[j] for v in coords) for j in range(3)]})
 for im in bpy.data.images:
  if im.size[0]:
   maximum=1024 if 'butterfly' in name else 2048
   if max(im.size)>maximum:
    f=maximum/max(im.size);im.scale(int(im.size[0]*f),int(im.size[1]*f))
   im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(CACHE/(name+'.blend')))
 report.append({'asset':name,'parts':parts})
 coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];low=Vector([min(v[j] for v in coords) for j in range(3)]);high=Vector([max(v[j] for v in coords) for j in range(3)]);center=(low+high)/2;size=max(high-low)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=500;s.render.resolution_y=500;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('Preview');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.21,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
 for loc in [(2,-3,4),(-3,-1,2)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=250;l.data.size=4;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.3
 for view,offset in [('front',(1.2,-3,1.4))]:
  cam.location=center+Vector(offset)*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(PREVIEW/(name+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
(ROOT/'build/asset_report05.json').write_text(json.dumps(report,indent=2));print('PREP03_COMPLETE',flush=True)
