import json,struct,io
from pathlib import Path
from PIL import Image
p=Path('build/web_handoff/jiuge_finale.glb')
b=p.read_bytes();jl=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+jl]);start=20+jl+8;binary=b[start:]
image_views={im['bufferView']:im for im in j.get('images',[]) if 'bufferView' in im}
out=bytearray()
for i,v in enumerate(j['bufferViews']):
 raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 if i in image_views:
  im=Image.open(io.BytesIO(raw));im.thumbnail((1536,1536))
  stream=io.BytesIO()
  if 'A' in im.getbands() and im.getchannel('A').getextrema()[0]<255:
   im.save(stream,format='PNG',optimize=True);mime='image/png'
  else:
   im.convert('RGB').save(stream,format='JPEG',quality=88);mime='image/jpeg'
  raw=stream.getvalue();image_views[i]['mimeType']=mime
 while len(out)%4:out.append(0)
 v['byteOffset']=len(out);v['byteLength']=len(raw);out.extend(raw)
j['buffers'][0]['byteLength']=len(out)
jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);out.extend(b'\0'*((-len(out))%4))
result=struct.pack('<III',0x46546c67,2,28+len(jb)+len(out))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(out),0x004e4942)+out
dest=Path('web/models/jiuge_finale.glb');dest.write_bytes(result);print(f'{len(b)/1e6:.1f} MB -> {len(result)/1e6:.1f} MB')
