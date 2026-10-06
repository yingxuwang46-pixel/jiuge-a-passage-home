import bpy, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'blender';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
collections={}
for name in ['01_Stone_Witnesses','02_Boat','03_Canyon','04_Water_Atmosphere','05_Lighting_Cameras']:
    c=bpy.data.collections.new(name); scene.collection.children.link(c); collections[name]=c
def move(o,coll):
    for c in list(o.users_collection): c.objects.unlink(o)
    collections[coll].objects.link(o)
def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m
assets={}
for p in sorted((ROOT/'build/assets').glob('*.blend')):
    with bpy.data.libraries.load(str(p),link=False) as (src,dst): dst.objects=src.objects
    o=next(o for o in dst.objects if o.type=='MESH'); assets[p.stem]=o
def instance(asset,name,loc,height=None,scale=None,rz=0,coll='03_Canyon'):
    proto=assets[asset];o=proto.copy();o.data=proto.data;collections[coll].objects.link(o);o.name=name
    coords=[v.co for v in o.data.vertices]
    low=min(v.z for v in coords);high=max(v.z for v in coords)
    if scale is None: scale=height/(high-low)
    o.scale=(scale,)*3 if isinstance(scale,(int,float)) else scale
    o.location=loc;o.location.z-=low*o.scale.z;o.rotation_mode='XYZ';o.rotation_euler.z=math.radians(rz)
    return o
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
def sphere(name,loc,radius,mat,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=radius,location=loc)
    o=bpy.context.object;o.name=name;move(o,'01_Stone_Witnesses');o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    if parent:o.parent=parent
    return o
# Pillars are linked instances, preserving true holes.
for name,loc,h,angle in [('Witness_Left',(-12,5,-.35),26,0),('Witness_Right',(17,13,-.35),29,-15),('Witness_Far_Left',(-5,68,-.3),23,10),('Witness_Far_Right',(11,48,-.3),25,-12)]:
    instance('pillar_complete_01',name,loc,height=h,rz=angle,coll='01_Stone_Witnesses')
hand=instance('eye_hand_01','Draped_Arm',(-17,7,-.7),height=17,rz=30,coll='01_Stone_Witnesses')
ivory=material('Weathered ivory eye',(.53,.57,.50),.29)
iris=material('Muted jade iris',(.10,.19,.17),.28)
it=iris.node_tree.nodes.new('ShaderNodeTexNoise');it.inputs['Scale'].default_value=32;it.inputs['Detail'].default_value=3
ir=iris.node_tree.nodes.new('ShaderNodeValToRGB');ir.color_ramp.elements[0].color=(.025,.05,.037,1);ir.color_ramp.elements[1].color=(.27,.34,.21,1)
iris.node_tree.links.new(it.outputs['Fac'],ir.inputs[0]);iris.node_tree.links.new(ir.outputs['Color'],iris.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
pupil=material('Deep pupil',(.008,.012,.010),.19)
eye=sphere('Eye_Pivot',(.172,-.401,.44),.048,ivory,hand)
# Sphere children use hand-local scale, not world units.
iris_obj=sphere('Iris',(0,-.045,0),.026,iris,eye);iris_obj.scale=(1,.20,1)
pupil_obj=sphere('Pupil',(0,-.051,0),.011,pupil,eye);pupil_obj.scale=(1,.18,1)
# Boat group, separate robe and canopy.
boat_root=bpy.data.objects.new('Boat_Rig',None);collections['02_Boat'].objects.link(boat_root)
boat_root.location=(2,22,0)
boat=instance('bird_boat_01','Bird_Boat',(0,0,-.16),scale=3.1,rz=-40,coll='02_Boat');boat.parent=boat_root
robe=instance('white_robe_01','Empty_White_Robe',(0,0,.40),height=1.25,rz=0,coll='02_Boat');robe.parent=boat_root
canopy=instance('red_umbrella_01','Red_Umbrella',(.12,.12,2.0),scale=1.6,rz=-12,coll='02_Boat');canopy.parent=boat_root
canopy.rotation_euler.x=math.radians(8)
wood=material('Umbrella dark wood',(.065,.038,.023),.65)
bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.026,depth=1.7,location=(.12,.12,1.45));pole=bpy.context.object;pole.name='Umbrella_Pole';pole.data.materials.append(wood);pole.parent=boat_root;move(pole,'02_Boat')
# Geological layers: overlapping silhouettes, submerged bases.
random.seed(14)
for side in [-1,1]:
    for i,y in enumerate([-1,22,47,76,110]):
        x=side*(36+i*3.7)
        instance('cliff_01' if i%2==0 else 'cliff_02',f'Cliff_{side}_{i}',(x,y,-5),scale=(40,37,75 if i<2 else 65),rz=side*(12+i*18))
    for i,y in enumerate([1,26,52]):
        instance('shore_rock_01',f'Shore_{side}_{i}',(side*(23+i*3),y,-3.6),scale=(19,24,15),rz=i*70)
for i,(x,y,h) in enumerate([(-37,80,64),(39,98,69),(-34,130,58),(44,153,66),(-55,165,85),(64,180,70)]):
    instance('peak_0'+str(i%3+1),f'Distant_Peak_{i}',(x,y,-7),height=h,rz=i*49)
# Cool and darken the rock materials without changing original textures.
seen=set()
for obj in collections['03_Canyon'].objects:
    for mat in obj.data.materials:
        if not mat or mat.name in seen or not mat.use_nodes:continue
        seen.add(mat.name); nodes=mat.node_tree.nodes; links=mat.node_tree.links
        bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bs and bs.inputs['Base Color'].is_linked:
            source=bs.inputs['Base Color'].links[0].from_socket
            mul=nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.43,.55,.58,1)
            links.new(source,mul.inputs[1]);links.new(mul.outputs[0],bs.inputs['Base Color'])
# Water with small physically shaded ripples.
water=material('River | gentle ripples',(.035,.085,.094),.18,.38)
n=water.node_tree.nodes;l=water.node_tree.links;p=n.get('Principled BSDF');p.inputs['IOR'].default_value=1.333
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.8;tex.inputs['Detail'].default_value=2
coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.075;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=1000,location=(0,120,0));o=bpy.context.object;o.name='River_Surface';o.data.materials.append(water);move(o,'04_Water_Atmosphere')
# Fog volume, lighter at foreground, building over distance.
fog=bpy.data.materials.new('Valley mist');fog.use_nodes=True;fog.node_tree.nodes.clear()
out=fog.node_tree.nodes.new('ShaderNodeOutputMaterial');v=fog.node_tree.nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.009;v.inputs['Color'].default_value=(.66,.76,.79,1);v.inputs['Anisotropy'].default_value=.25;v.inputs['Emission Strength'].default_value=.004;v.inputs['Emission Color'].default_value=(.65,.75,.78,1);fog.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,145,55));o=bpy.context.object;o.name='Valley_Mist';o.scale=(240,246,115);o.data.materials.append(fog);o.display_type='WIRE';move(o,'04_Water_Atmosphere')
# Soft cloud-colored sky and raking light.
world=bpy.data.worlds.new('Pale overcast sky');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.75,.80,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
wn=world.node_tree.nodes;wl=world.node_tree.links
sky=wn.new('ShaderNodeBackground');sky.inputs[0].default_value=(.80,.87,.89,1);sky.inputs[1].default_value=1.2
lp=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');wl.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(wn['Background'].outputs[0],mix.inputs[1]);wl.new(sky.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn['World Output'].inputs['Surface'])
bpy.ops.object.light_add(type='SUN',location=(-30,-20,65));sun=bpy.context.object;sun.name='Veiled_Sun';sun.data.energy=2.8;sun.data.angle=.25;aim(sun,(4,22,0));move(sun,'05_Lighting_Cameras')
bpy.ops.object.light_add(type='AREA',location=(-8,-15,38));light=bpy.context.object;light.name='Soft_Foreground';light.data.energy=2300;light.data.shape='DISK';light.data.size=35;aim(light,(-4,12,12));move(light,'05_Lighting_Cameras')
bpy.ops.object.camera_add(location=(0,-45,3.0));cam=bpy.context.object;cam.name='Camera_Hero';cam.data.lens=28;cam.data.clip_end=1500;aim(cam,(1,29,19));scene.camera=cam;move(cam,'05_Lighting_Cameras')
# Editable route: a short, slow passage through the witnesses.
curve=bpy.data.curves.new('Ferry route','CURVE');curve.dimensions='3D';spline=curve.splines.new('BEZIER');spline.bezier_points.add(3)
for p,co in zip(spline.bezier_points,[(2,15,.0),(1,26,.0),(0,43,.0),(1,58,.0)]):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
route=bpy.data.objects.new('Ferry_Route',curve);collections['02_Boat'].objects.link(route);route.hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.max_bounces=5;scene.cycles.volume_bounces=1
scene.render.resolution_x=1200;scene.render.resolution_y=518;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.4
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'scene_preview_v01.png')
scene.render.fps=24;scene.frame_end=720
for frame,loc in [(1,(2,22,0)),(240,(1.6,27,0)),(480,(.8,34,0)),(720,(1,42,0))]:
    boat_root.location=loc;boat_root.keyframe_insert(data_path='location',frame=frame)
scene.frame_set(1)
scene['project']='九歌 · 渡无归者';scene['stage']='First scene assembly; web effects to be adapted separately'
scene['source_assets']=str(ROOT/'source-assets/assets')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=2000
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'jiuge_canyon_v01.blend'))
bpy.ops.render.render(write_still=True)
print('SCENE_READY',flush=True)
