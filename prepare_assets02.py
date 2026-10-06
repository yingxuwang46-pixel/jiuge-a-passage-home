import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source-assets/assets02'
CACHE=ROOT/'build/assets02'
PREVIEW=ROOT/'build/previews02'
CACHE.mkdir(parents=True,exist_ok=True); PREVIEW.mkdir(parents=True,exist_ok=True)
report=[]
for p in sorted(SOURCE.glob('*.glb')):
    if p.stem not in {'white_tree_01','hanging_hand_01','hanging_hand_02','red_robed_figure_01','cave_cliff_01','sloping_rock_01'}: continue
    name=p.name.replace('.glb.glb','.glb')[:-4]
    if (CACHE/(name+'.blend')).exists():
        print('CACHED',name,flush=True); continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(p))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1: bpy.ops.object.join()
    obj=bpy.context.object; obj.name=name
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    before=len(obj.data.polygons)
    target=100000 if 'tree' in name else 65000 if 'figure' in name else 12000 if 'hand' in name else 45000
    if before>target:
        m=obj.modifiers.new('Working mesh reduction','DECIMATE'); m.ratio=target/before
        bpy.ops.object.modifier_apply(modifier=m.name)
    for face in obj.data.polygons: face.use_smooth=True
    for im in bpy.data.images:
        if im.size[0]>0:
            maximum=2048 if ('tree' in name or 'figure' in name) else 1024
            if max(im.size)>maximum:
                factor=maximum/max(im.size); im.scale(int(im.size[0]*factor),int(im.size[1]*factor))
            im.pack()
    report.append(dict(name=name,before=before,after=len(obj.data.polygons),dimensions=list(obj.dimensions)))
    bpy.ops.wm.save_as_mainfile(filepath=str(CACHE/(name+'.blend')))
    s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=12
    s.cycles.use_denoising=True
    s.render.resolution_x=440; s.render.resolution_y=440; s.render.resolution_percentage=100
    s.world=bpy.data.worlds.new('Preview world'); s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    for loc,energy,size in [((2,-3,4),350,4),((-3,-1,2),180,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=size
        l.rotation_euler=(Vector((0,0,.4))-l.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(); camera=bpy.context.object; s.camera=camera; camera.data.type='ORTHO';camera.data.ortho_scale=1.35
    for view,loc in [('front',(1.3,-3,1.5)),('back',(-1.3,3,1.5))]:
        camera.location=loc; camera.rotation_euler=(Vector((0,0,.45))-camera.location).to_track_quat('-Z','Y').to_euler()
        s.render.filepath=str(PREVIEW/(name+'_'+view+'.png')); bpy.ops.render.render(write_still=True)
    print('FINISHED',report[-1],flush=True)
(ROOT/'build/asset_report02.json').write_text(json.dumps(report,indent=2))
