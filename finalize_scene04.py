import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(root/'blender/jiuge_ritual_v01.blend'));s=bpy.context.scene;cam=s.camera
report=json.loads((root/'build/scene04_report.json').read_text());queue=Vector(report['anchors']['Queue_Target']);sun=Vector(report['anchors']['Sun_Anchor']);y=queue.z
shots=[(1,(13,-58,16),(-1,5,13)),(230,(7,-36,13),(-9,0,7)),(420,(-4,-22,y+5),queue),(570,(-14,-12,y+3),queue),(720,(-24,-12,y+3.5),queue),(860,(-27,-19,y+5),queue),(1020,(-15,-29,y+8),queue.lerp(sun,.65))]
for f,pos,target in shots:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
 s.timeline_markers.new('View_'+str(f),frame=f)
s.render.fps=30;s.frame_end=1020;s.frame_set(1)
s['web_controls']='Approach the Procession / Awaken the Sun / Hold to Awaken';s['camera_note']='Editable 34-second camera passage; browser uses a centripetal spline and smooth target interpolation.'
for scr in bpy.data.screens:
 for a in scr.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/jiuge_ritual_v01.blend'))
print('FINAL04_SAVED')
