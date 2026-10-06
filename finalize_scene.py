import bpy, math, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent; out=root/'blender'
bpy.ops.wm.open_mainfile(filepath=str(out/'jiuge_canyon_v01.blend'))
s=bpy.context.scene
hand=bpy.data.objects['Draped_Arm']; factor=19/17;hand.scale*=factor;hand.location=(-13,8,-1);hand.rotation_euler.z=math.radians(45)
cam=s.camera;cam.rotation_euler=(Vector((1,29,17))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=1800;s.render.resolution_y=776;s.cycles.samples=48
s.render.filepath=str(out/'jiuge_canyon_preview.png')
# Add useful secondary cameras for inspection without altering the hero shot.
for name,loc,target,lens in [('Camera_Boat_Detail',(6,15,3),(2,22,1),45),('Camera_Eye_Detail',(1,-12,12),(-3,1,10),42)]:
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);bpy.data.collections['05_Lighting_Cameras'].objects.link(o);o.location=loc;data.lens=lens;data.clip_end=1000;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0
            area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.overlay.show_overlays=False
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active=s.camera
bpy.ops.wm.save_as_mainfile(filepath=str(out/'jiuge_canyon_v02.blend'))
bpy.ops.render.render(write_still=True)
# Export a geometry / material handoff. Blender volumes and water remain in .blend.
export=root/'build/web_handoff';export.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for name in ['01_Stone_Witnesses','02_Boat','03_Canyon']:
    for o in bpy.data.collections[name].objects:
        if o.type in {'MESH','EMPTY'}:o.select_set(True)
cam.select_set(True)
# Convert the rock tint to the exporter's supported texture-times-color setup.
for m in bpy.data.materials:
    if not m.use_nodes:continue
    for n in list(m.node_tree.nodes):
        if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY':
            target=n.outputs[0].links[0].to_socket if n.outputs[0].is_linked else None
            source=n.inputs[1].links[0].from_socket if n.inputs[1].is_linked else None
            if target and source:m.node_tree.links.new(source,target)
            m['web_color_multiplier']=[.43,.55,.58]
bpy.ops.export_scene.gltf(filepath=str(export/'jiuge_canyon.glb'),export_format='GLB',use_selection=True,export_cameras=True,export_extras=True,export_animations=True)
report={'unique_mesh_triangles':sum(len(m.polygons) for m in set(o.data for o in s.objects if o.type=='MESH')),'scene_instances':len([o for o in s.objects if o.type=='MESH']),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'missing_images':[i.name for i in bpy.data.images if i.type=='IMAGE' and not i.has_data],'camera':list(cam.location),'boat_animation_frames':[1,720],'limitations':['Web water, fog, lighting and procedural iris require implementation in Three.js.','The original Tripo cliff shapes are more block-like than the target image.']}
(export/'inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('FINAL_REPORT',report,flush=True)
