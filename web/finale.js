import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createAtmosphere} from './atmosphere.js';
import {mountainMist} from './mountain-atmosphere.js';

export function createFinaleChapter(renderer,water){
 const scene=new THREE.Scene();scene.background=new THREE.Color('#a7bec4');scene.fog=new THREE.FogExp2('#9eb8be',.006);
 const camera=new THREE.PerspectiveCamera(38,2,.12,1100),air=createAtmosphere(scene),mist=mountainMist(scene);
 for(const o of scene.children){if(o.material?.uniforms?.uOpacity){o.material.uniforms.uOpacity.value*=1.5;}}
 scene.add(new THREE.HemisphereLight(0xd7e8e8,0x142b31,1.6));const sun=new THREE.DirectionalLight(0xffeedc,3);sun.position.set(-28,55,25);scene.add(sun);
 sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-45,right:45,top:50,bottom:-40,near:1,far:170});sun.shadow.normalBias=.07;
 const hud=document.createElement('section');hud.id='finale-ui';hud.hidden=true;hud.innerHTML=`<div class="chapter-label">V · WHAT REMAINS IN BLOOM</div><p id="finale-line" aria-live="polite">Touch three flowers. Offer the river a remembrance.</p><div id="finale-count" aria-live="polite">0 / 3</div><div class="finale-actions"><button id="finale-touch">Touch a Flower</button><button id="finale-reset">Begin Again</button><button id="finale-return">Return to the Sun</button><button id="finale-replay" hidden>Replay the Journey</button></div><small>Click the larger red flowers · Drag to look around</small>`;document.body.append(hud);
 const q=s=>hud.querySelector(s),flowers=[],targets=[],ripples=[],ray=new THREE.Raycaster(),mouse=new THREE.Vector2(),aim=new THREE.Vector2(),view=new THREE.Vector2();
 let loaded=false,active=false,promise,error,rig,bloom,elapsed=0,count=0,bloomTime=-1,complete=false,drag=null,dragged=false;
 const ease=t=>{t=THREE.MathUtils.clamp(t,0,1);return t*t*(3-2*t);};
 const ringGeo=new THREE.RingGeometry(.95,1,64);
 function ripple(x,z){for(let i=0;i<3;i++){const m=new THREE.Mesh(ringGeo,new THREE.MeshBasicMaterial({color:0xbfd3ce,transparent:true,opacity:0,depthWrite:false,side:THREE.DoubleSide}));m.rotation.x=-Math.PI/2;m.position.set(x,.035,z);scene.add(m);ripples.push({mesh:m,age:-i*.22});}}
 function touch(f){if(!active||!loaded||f.userData.touched||count===3)return;f.userData.touched=true;f.userData.touchTime=elapsed;ripple(f.position.x,f.position.z);count++;q('#finale-count').textContent=`${count} / 3`;q('#finale-line').textContent=count===3?'What cannot return may still bloom.':'A quiet offering. Touch another flower.';if(count===3){bloomTime=0;q('#finale-touch').disabled=true;}}
 function load(){if(promise)return promise;promise=new GLTFLoader().loadAsync('./models/jiuge_finale.glb').then(g=>{
  scene.add(g.scene);g.scene.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;for(const m of [].concat(o.material)){m.side=THREE.DoubleSide;m.roughness=Math.max(.58,m.roughness??.8);if(m.map)m.map.anisotropy=4;}}});
  rig=g.scene.getObjectByName('Final_Boat_Rig');bloom=g.scene.getObjectByName('Umbrella_Bloom');const template=g.scene.getObjectByName('Flower_Template');if(!rig||!bloom||!template)throw Error('Missing finale assets');template.removeFromParent();
  function flower(x,z,s,interactive=false){const f=template.clone();f.position.set(x,.045,z);f.scale.setScalar(s);f.rotation.y=x*2;f.userData={size:s,phase:x+z,touched:false,touchTime:-100,interactive};scene.add(f);flowers.push(f);if(interactive){targets.push(f);const hit=new THREE.Mesh(new THREE.SphereGeometry(.85,12,8),new THREE.MeshBasicMaterial({visible:false}));hit.name='FlowerHit';f.add(hit);hit.scale.setScalar(1/s);hit.userData.flower=f;}return f;}
  flower(-5.2,3,1.15,true);flower(4.5,5,1.1,true);flower(6.8,-4,1.15,true);
  let seed=29;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};for(let i=0;i<52;i++){const x=(rnd()-.5)*46,z=-48+rnd()*69;if(Math.abs(x)<4&&z>-9&&z<0)continue;flower(x,z,.25+rnd()*.34);}
  loaded=true;reset();return true;
 }).catch(e=>{error=e;promise=null;console.error('Chapter V:',e);return false;});return promise;}
 function reset(){elapsed=0;count=0;bloomTime=-1;complete=false;aim.set(0,0);view.set(0,0);if(bloom){bloom.visible=false;bloom.scale.setScalar(.001);}for(const f of flowers){f.userData.touched=false;f.userData.touchTime=-100;}for(const r of ripples){r.mesh.removeFromParent();r.mesh.material.dispose();}ripples.length=0;q('#finale-count').textContent='0 / 3';q('#finale-line').textContent='Touch three flowers. Offer the river a remembrance.';q('#finale-touch').disabled=false;q('#finale-replay').hidden=true;}
 q('#finale-touch').onclick=()=>{const f=targets.find(f=>!f.userData.touched);if(f)touch(f);};q('#finale-reset').onclick=reset;q('#finale-replay').onclick=()=>location.assign(location.pathname);
 renderer.domElement.addEventListener('pointerdown',e=>{if(!active)return;drag={x:e.clientX,y:e.clientY,ax:aim.x,ay:aim.y};dragged=false;renderer.domElement.setPointerCapture(e.pointerId);});
 renderer.domElement.addEventListener('pointermove',e=>{if(!active||!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>5)dragged=true;aim.set(THREE.MathUtils.clamp(drag.ax+dx*.004,-.55,.55),THREE.MathUtils.clamp(drag.ay+dy*.003,-.15,.3));});
 for(const event of ['pointerup','pointercancel'])renderer.domElement.addEventListener(event,()=>drag=null);
 renderer.domElement.addEventListener('click',e=>{if(!active||!loaded||dragged)return;const r=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);ray.setFromCamera(mouse,camera);const hits=ray.intersectObjects(targets,true);if(hits.length){let f=hits[0].object;while(f&&!targets.includes(f))f=f.parent;if(f)touch(f);}});
 function update(dt,time){if(!active||!loaded)return;elapsed+=dt;air.update(time);mist.update(time);view.lerp(aim,1-Math.exp(-dt*5));rig.position.y=Math.sin(time*.8)*.035;rig.rotation.z=Math.sin(time*.65)*.006;
  for(const f of flowers){const age=elapsed-f.userData.touchTime,k=age<3?Math.exp(-age*1.6):0;f.position.y=.055+Math.sin(time*1.3+f.userData.phase)*.025;f.rotation.x=Math.sin(time*.9+f.userData.phase)*.045+Math.sin(age*8)*k*.24;f.rotation.z=Math.cos(time*.8+f.userData.phase)*.05;}
  for(let i=ripples.length-1;i>=0;i--){const r=ripples[i];r.age+=dt;r.mesh.scale.setScalar(.25+Math.max(0,r.age)*1.25);r.mesh.material.opacity=r.age<0?0:.24*Math.max(0,1-r.age/2.6);if(r.age>2.6){r.mesh.removeFromParent();r.mesh.material.dispose();ripples.splice(i,1);}}
  let end=0;if(bloomTime>=0){bloomTime+=dt;const t=Math.max(0,bloomTime-.65);bloom.visible=true;bloom.scale.set(Math.max(.005,ease((t-.65)/3)),Math.max(.005,ease(t/2.6)),Math.max(.005,ease((t-.65)/3)));end=ease((t-4)/3);if(t>7&&!complete){complete=true;q('#finale-line').textContent='For those who cannot return, let something bloom.';q('#finale-replay').hidden=false;window.dispatchEvent(new CustomEvent('jiuge:chapter-complete',{detail:{chapter:5}}));}}
  const entry=ease(elapsed/2.8),radius=THREE.MathUtils.lerp(39,31,entry)+end*6,angle=.16-entry*.13+Math.sin(elapsed*.12)*.055+view.x-(bloomTime>0?ease(bloomTime/5)*.17:0);camera.position.set(Math.sin(angle)*radius,5.4+end*1.5+view.y*12,Math.cos(angle)*radius-4);camera.lookAt(0,5+end*2,-6-end*8);
  camera.aspect=renderer.domElement.clientWidth/renderer.domElement.clientHeight;camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(31))/camera.aspect));camera.updateProjectionMatrix();
  renderer.domElement.dataset.chapter='5';renderer.domElement.dataset.flowersTouched=String(count);renderer.domElement.dataset.finaleComplete=String(complete);renderer.domElement.dataset.umbrellaGrowth=bloom.scale.y.toFixed(3);
 }
 return {scene,camera,load,get loaded(){return loaded;},get error(){return error;},enter(){active=true;hud.hidden=false;water.visible=true;water.position.y=0;scene.add(water);},leave(){active=false;hud.hidden=true;drag=null;},update,onReturn(fn){q('#finale-return').onclick=fn;}};
}
