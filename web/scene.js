import {createFinaleChapter} from './finale.js';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Water } from 'three/addons/objects/Water.js';
import { createAtmosphere, addHeightHaze } from './atmosphere.js';
import { createKeeperChapter } from './keeper.js';
import { createMountainChapter } from './mountain.js';
import {createRitualChapter} from './ritual.js';

const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
document.body.prepend(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#b3c6c9');scene.fog=new THREE.FogExp2('#acbfc2',.008);
const atmosphere=createAtmosphere(scene);
const camera=new THREE.PerspectiveCamera(33,innerWidth/innerHeight,.1,900);
scene.add(new THREE.HemisphereLight(0xcde1e5,0x182828,1.15));
const sun=new THREE.DirectionalLight(0xfff4de,3.2);sun.position.set(-35,65,25);scene.add(sun);
sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-60,right:60,top:65,bottom:-65,near:1,far:210});sun.shadow.bias=-.00025;sun.shadow.normalBias=.1;

// Procedural normal map keeps the water self-contained and available offline.
const n=256,data=new Uint8Array(n*n*4);
for(let y=0;y<n;y++)for(let x=0;x<n;x++){let i=(y*n+x)*4,dx=0,dy=0;for(let k=1;k<=12;k++){const a=k*2.39996,fx=Math.round(Math.cos(a)*(3+k)),fy=Math.round(Math.sin(a)*(3+k)),phase=(x*fx+y*fy)*Math.PI*2/n+k*1.7;dx+=Math.cos(phase)*Math.cos(a)*5;dy+=Math.cos(phase)*Math.sin(a)*5;}data[i]=128+dx;data[i+1]=128+dy;data[i+2]=252;data[i+3]=255;}
const normals=new THREE.DataTexture(data,n,n);normals.wrapS=normals.wrapT=THREE.RepeatWrapping;normals.magFilter=THREE.LinearFilter;normals.minFilter=THREE.LinearMipmapLinearFilter;normals.generateMipmaps=true;normals.needsUpdate=true;
const water=new Water(new THREE.PlaneGeometry(1300,1300),{textureWidth:1024,textureHeight:1024,waterNormals:normals,sunDirection:sun.position.clone().normalize(),sunColor:0xdde9db,waterColor:0x103239,distortionScale:.65,fog:true});
water.rotation.x=-Math.PI/2;water.position.z=-130;scene.add(water);
water.material.uniforms.size.value=5.5;
water.material.fragmentShader=water.material.fragmentShader.replace('#include <tonemapping_fragment>','gl_FragColor.rgb *= mix(vec3(.23,.38,.41),vec3(.62,.77,.79),smoothstep(8.,125.,distance));\n#include <tonemapping_fragment>');
const chapter2=createKeeperChapter(renderer,water),chapter3=createMountainChapter(renderer,water),chapter4=createRitualChapter(renderer),chapter5=createFinaleChapter(renderer,water);
const veil=document.createElement('div');veil.id='chapter-veil';veil.setAttribute('aria-hidden','true');veil.innerHTML='<p>Beyond the mist, a keeper waits.</p>';document.body.append(veil);
const enterButton=document.createElement('button');enterButton.id='enter-keeper';enterButton.textContent='Enter the Grove';enterButton.hidden=true;document.querySelector('footer').append(enterButton);
let chapter=1,transition=null,transitionTime=0,transitionAttempted=false,transitionTarget=2;
const intro=document.querySelector('header .intro'),context=document.querySelector('header .context');
async function enterKeeper(){
 if(transition||chapter===2)return;
 transitionTarget=2;transition='out';transitionTime=0;held=false;auto=false;veil.classList.add('active');veil.setAttribute('aria-hidden','false');veil.querySelector('p').textContent='Beyond the mist, a keeper waits.';
 const ok=await chapter2.load();
 if(!ok){transition=null;veil.classList.remove('active');veil.setAttribute('aria-hidden','true');veil.style.opacity=0;enterButton.hidden=false;enterButton.textContent='Retry the Crossing';document.querySelector('#caption').textContent='The grove could not load. Please try again.';}
}
enterButton.onclick=enterKeeper;
chapter2.onReturn(()=>{chapter2.leave();chapter=1;water.position.y=0;scene.add(water);progress=0;speed=0;auto=false;held=false;transitionAttempted=false;autoButton.textContent='Begin the Crossing';enterButton.hidden=true;document.querySelector('footer').hidden=false;document.querySelector('#caption').hidden=false;document.querySelector('#line').hidden=false;intro.hidden=false;context.textContent='Inspired by ancient Chu ritual poetry.';history.replaceState(null,'',location.pathname);renderer.domElement.dataset.chapter='1';});

async function enterMountain(){
 if(transition||chapter===3)return;
 transitionTarget=3;transition='out';transitionTime=0;held=false;auto=false;veil.classList.add('active');veil.setAttribute('aria-hidden','false');veil.querySelector('p').textContent='Above the river, a memory takes wing.';
 const ok=await chapter3.load();if(!ok){transition=null;veil.classList.remove('active');veil.style.opacity=0;veil.setAttribute('aria-hidden','true');document.querySelector('#keeper-line').textContent='The mountain could not load. Choose Follow the Butterfly to retry.';}
}
chapter2.onContinue(enterMountain);
chapter3.onReturn(async()=>{if(transition)return;await chapter2.load();chapter3.leave();chapter=2;chapter2.enter(true);context.textContent='The Keeper of Remembrance';history.replaceState(null,'',location.pathname+'#keeper');});
window.addEventListener('jiuge:chapter-complete',e=>{if(e.detail.chapter===2)chapter3.load();});

async function enterRitual(){
 if(transition||chapter===4)return;
 transitionTarget=4;transition='out';transitionTime=0;held=false;auto=false;veil.classList.add('active');veil.setAttribute('aria-hidden','false');veil.querySelector('p').textContent='Gather beneath the silent sun.';
 const ok=await chapter4.load();if(!ok){transition=null;veil.classList.remove('active');veil.style.opacity=0;veil.setAttribute('aria-hidden','true');document.querySelector('#mountain-line').textContent='The procession could not load. Please try again.';}
}
chapter3.onContinue(enterRitual);
chapter4.onReturn(async()=>{if(transition)return;const ok=await chapter3.load();if(!ok)return;chapter4.leave();chapter=3;chapter3.enter();context.textContent='Where Memory Takes Wing';history.replaceState(null,'',location.pathname+'#mountain');});
window.addEventListener('jiuge:chapter-complete',e=>{if(e.detail.chapter===3)chapter4.load();});
async function enterFinale(){
 if(transition||chapter===5)return;
 transitionTarget=5;transition='out';transitionTime=0;held=false;auto=false;veil.classList.add('active');veil.setAttribute('aria-hidden','false');veil.querySelector('p').textContent='One last offering, upon the water.';
 const ok=await chapter5.load();if(!ok){transition=null;veil.classList.remove('active');veil.style.opacity=0;veil.setAttribute('aria-hidden','true');document.querySelector('#ritual-line').textContent='The river could not load. Please try again.';}
}
chapter4.onContinue(enterFinale);
chapter5.onReturn(async()=>{if(transition)return;const ok=await chapter4.load();if(!ok)return;chapter5.leave();chapter=4;chapter4.enter();context.textContent='Beneath the Silent Sun';history.replaceState(null,'',location.pathname+'#ritual');});
window.addEventListener('jiuge:chapter-complete',e=>{if(e.detail.chapter===4)chapter5.load();});


let boat,eye,baseEye,ready=false,held=false,auto=false,progress=0,speed=0,high=false;
const pointer=new THREE.Vector2(),look=new THREE.Vector2();
// Bow initially faces left: a broad quarter-turn, then a clear channel between pillars.
const path=new THREE.CurvePath();
path.add(new THREE.CubicBezierCurve3(new THREE.Vector3(2,0,-22),new THREE.Vector3(-3.52,0,-22),new THREE.Vector3(-8,0,-26.48),new THREE.Vector3(-8,0,-32)));
path.add(new THREE.CubicBezierCurve3(new THREE.Vector3(-8,0,-32),new THREE.Vector3(-8,0,-49),new THREE.Vector3(2,0,-53),new THREE.Vector3(2,0,-72)));
path.add(new THREE.LineCurve3(new THREE.Vector3(2,0,-72),new THREE.Vector3(2,0,-118)));
const boatMaterials=[],eyeTarget=new THREE.Vector3(),eyeDirection=new THREE.Vector3(),eyeRestDirection=new THREE.Vector3(0,0,1),eyeRotation=new THREE.Quaternion();
const status=document.querySelector('#status');
new GLTFLoader().load('./models/jiuge_canyon.glb',g=>{
 scene.add(g.scene);boat=g.scene.getObjectByName('Boat_Rig');eye=g.scene.getObjectByName('Eye_Pivot');baseEye=eye.quaternion.clone();
 const processed=new Set();g.scene.traverse(o=>{if(o.isMesh){o.frustumCulled=true;o.castShadow=true;o.receiveShadow=true;for(const m of [].concat(o.material)){if(processed.has(m))continue;processed.add(m);const tint=m.userData.web_color_multiplier;if(tint)m.color.multiply(new THREE.Color(...tint));m.roughness=Math.max(m.roughness??.8,.55);if(m.map)m.map.anisotropy=4;} }});
 const robe=g.scene.getObjectByName('Empty_White_Robe');if(robe)robe.traverse(o=>{if(o.isMesh)o.material=new THREE.MeshStandardMaterial({color:0xdddcd0,roughness:.95});});
 const iris=g.scene.getObjectByName('Iris');if(iris){iris.material=new THREE.MeshStandardMaterial({color:0x708778,roughness:.35});}
 const pupil=g.scene.getObjectByName('Pupil');if(pupil)pupil.material=new THREE.MeshStandardMaterial({color:0x081215,roughness:.17});
 boat.traverse(o=>{if(o.isMesh){o.material=[].concat(o.material).map(m=>{const copy=m.clone();copy.transparent=true;boatMaterials.push(copy);return copy;});if(o.material.length===1)o.material=o.material[0];}});
 g.scene.traverse(o=>{if(o.isMesh)for(const m of [].concat(o.material)){addHeightHaze(m);m.needsUpdate=true;}});
 ready=true;document.querySelector('#loading').style.opacity=0;setTimeout(()=>document.querySelector('#loading').remove(),1100);if(location.hash==='#keeper')enterKeeper();else if(location.hash==='#mountain')enterMountain();else if(location.hash==='#ritual')enterRitual();else if(location.hash==='#finale')enterFinale();
},e=>{if(e.total)status.textContent=`The world is emerging from the mist · ${Math.round(e.loaded/e.total*100)}%`;},e=>{status.textContent='Unable to load the world. Please refresh and check the local server.';console.error(e);});

const hold=document.querySelector('#hold');hold.addEventListener('pointerdown',e=>{held=true;hold.setPointerCapture(e.pointerId);});
for(const evt of ['pointerup','pointercancel','lostpointercapture'])hold.addEventListener(evt,()=>held=false);
addEventListener('keydown',e=>{if(e.code==='Space'&&!['BUTTON','INPUT'].includes(document.activeElement.tagName)){e.preventDefault();held=true;}});
addEventListener('keyup',e=>{if(e.code==='Space')held=false;});addEventListener('blur',()=>held=false);document.addEventListener('visibilitychange',()=>{if(document.hidden)held=false;});
addEventListener('pointermove',e=>{pointer.set(e.clientX/innerWidth*2-1,e.clientY/innerHeight*2-1);});
const autoButton=document.querySelector('#auto');autoButton.onclick=()=>{auto=!auto;autoButton.textContent=auto?'Pause':'Begin the Crossing';};
document.querySelector('#reset').onclick=()=>{progress=0;speed=0;held=false;auto=false;autoButton.textContent='Begin the Crossing';};
document.querySelector('#quality').onclick=e=>{high=!high;renderer.setPixelRatio(Math.min(devicePixelRatio,high?2:1.5));e.target.textContent=`Quality: ${high?'High':'Standard'}`;};
function resize(){const h=Math.min(innerHeight,innerWidth/1.65);renderer.setSize(innerWidth,h);renderer.domElement.style.position='absolute';renderer.domElement.style.top=`${(innerHeight-h)/2}px`;camera.aspect=innerWidth/h;camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(32))/camera.aspect));camera.updateProjectionMatrix();}addEventListener('resize',resize);resize();
const clock=new THREE.Clock(),worldBoat=new THREE.Vector3(),worldEye=new THREE.Vector3();let time=0,frames=0,reportTime=0;
function frame(){requestAnimationFrame(frame);const dt=Math.min(clock.getDelta(),.05);time+=dt;
 look.lerp(pointer,1-Math.exp(-dt*2));
 const travel=THREE.MathUtils.smoothstep(progress,0,1),arc=Math.sin(progress*Math.PI);
 camera.position.set(arc*9+travel*4+look.x*2,3+arc*3+travel*2-look.y*.5,45-travel*55);
 camera.lookAt(1+look.x*2,17*(1-travel)+travel*3-look.y,-29-travel*45);
 water.material.uniforms.time.value=time*.22;atmosphere.update(time);
 if(ready&&chapter===1){speed=THREE.MathUtils.damp(speed,(held||auto)&&progress<1&&!transition?1/32:0,held||auto?1.7:2.5,dt);progress=Math.min(1,progress+speed*dt);boat.position.copy(path.getPointAt(progress));boat.position.y+=Math.sin(time*1.2)*.035;
 const tangent=path.getTangentAt(Math.min(progress,.9999));boat.rotation.set(Math.sin(time*.9)*.006,Math.atan2(tangent.z,-tangent.x),Math.sin(time*.8)*.009);
 const dissolve=1-THREE.MathUtils.smoothstep(progress,.83,.98);boatMaterials.forEach(m=>{m.opacity=dissolve;});
 // Gentle local eye movement; range is limited so it remains inside its stone socket.
 boat.getWorldPosition(worldBoat);
 // Keep the eye seated; project a true target direction onto a 30-degree gaze cone.
 eyeTarget.copy(camera.position).lerp(worldBoat,THREE.MathUtils.smoothstep(progress,0,.22));
 eye.parent.worldToLocal(eyeTarget);eyeDirection.copy(eyeTarget).sub(eye.position).normalize();
 eyeRotation.setFromUnitVectors(eyeRestDirection,eyeDirection);const angle=eyeRotation.angleTo(new THREE.Quaternion());
 if(angle>.52)eyeRotation.slerpQuaternions(new THREE.Quaternion(),eyeRotation,.52/angle);
 eye.quaternion.slerp(eyeRotation,1-Math.exp(-dt*2.2));
 document.querySelector('#line').style.width=`${progress*100}%`;hold.textContent=progress>=1?'Arrived':'Hold to Sail';document.querySelector('#caption').textContent=progress>.96?'Some journeys end in a place. Others end in being remembered.':progress>.12?'':'Think of someone you wish to bring home.';
 if(progress>.25&&!chapter2.loaded&&!chapter2.error)chapter2.load();
 if(progress>=1&&!transitionAttempted){transitionAttempted=true;enterKeeper();}
 }
 if(transition){transitionTime+=dt;if(transition==='out'){veil.style.opacity=Math.min(transitionTime/2.2,1);if(transitionTime>=2.2&&({2:chapter2,3:chapter3,4:chapter4,5:chapter5}[transitionTarget].loaded)){chapter2.leave();chapter3.leave();chapter4.leave();chapter5.leave();chapter=transitionTarget;({2:chapter2,3:chapter3,4:chapter4,5:chapter5}[chapter]).enter();document.querySelector('footer').hidden=true;document.querySelector('#caption').hidden=true;document.querySelector('#line').hidden=true;intro.hidden=true;context.textContent={2:'The Keeper of Remembrance',3:'Where Memory Takes Wing',4:'Beneath the Silent Sun',5:'What Remains in Bloom'}[chapter];history.replaceState(null,'',location.pathname+({2:'#keeper',3:'#mountain',4:'#ritual',5:'#finale'}[chapter]));transition='in';transitionTime=0;}}else{veil.style.opacity=Math.max(0,1-transitionTime/2.2);if(transitionTime>2.2){transition=null;veil.classList.remove('active');veil.setAttribute('aria-hidden','true');}}}
 if(chapter===5){chapter5.update(dt,time);renderer.render(chapter5.scene,chapter5.camera);}else if(chapter===4){chapter4.update(dt,time);renderer.render(chapter4.scene,chapter4.camera);}else if(chapter===3){chapter3.update(dt,time);renderer.render(chapter3.scene,chapter3.camera);}else if(chapter===2){chapter2.update(dt,time,pointer);renderer.render(chapter2.scene,chapter2.camera);}else renderer.render(scene,camera);
 frames++;if(time-reportTime>1){renderer.domElement.dataset.progress=progress.toFixed(4);renderer.domElement.dataset.fps=Math.round(frames/(time-reportTime));renderer.domElement.dataset.ready=String(ready);reportTime=time;frames=0;}}
frame();
