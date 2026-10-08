import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { createAtmosphere, addHeightHaze } from './atmosphere.js';

// Chapter II keeps its own scene and state; Chapter I remains intact.
export function createKeeperChapter(renderer,water){
 const scene=new THREE.Scene();scene.background=new THREE.Color('#adbec2');scene.fog=new THREE.FogExp2('#adbec2',.012);
 const atmosphere=createAtmosphere(scene),camera=new THREE.PerspectiveCamera(40,2,.1,900);
 scene.add(new THREE.HemisphereLight(0xcbdce1,0x142626,1.1));
 const sun=new THREE.DirectionalLight(0xf5e7ce,2.8);sun.position.set(12,32,20);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-25,right:25,top:25,bottom:-25,near:1,far:110});sun.shadow.normalBias=.07;sun.shadow.bias=-.0002;scene.add(sun);
 const keeperLight=new THREE.PointLight(0xe1aa77,0,13,2);keeperLight.position.set(1.4,5,3.4);scene.add(keeperLight);
 const hud=document.createElement('section');hud.id='keeper-ui';hud.hidden=true;
 hud.innerHTML=`<div class="chapter-label">II · THE KEEPER OF REMEMBRANCE</div><p id="keeper-line" aria-live="polite">Some farewells were left unfinished.</p><div class="ritual-progress" aria-label="Three offerings"><i></i><i></i><i></i></div><div class="keeper-actions"><button id="take-hand">Take a Hand</button><button id="offer-hand" hidden>Offer to the Keeper</button><button id="hang-hand" hidden>Hang on the Tree</button><button id="repeat-ritual" hidden>Remember Again</button><button id="continue-mountain" hidden>Follow the Butterfly</button><button id="return-river">Return to the River</button></div><small id="keeper-hint">Choose the pale hand by the water.</small>`;
 document.body.append(hud);
 const q=id=>hud.querySelector('#'+id),line=q('keeper-line'),hint=q('keeper-hint');
 let model,pickup,halo,offering,keeper,branchMarker,anchors=[],hands=[],state='loading',round=0,anim=0,mode='',active=false,loaded=false,error=null,loadPromise=null,chapterTime=0;
 const pickupStart=new THREE.Vector3(4.5,4,6),offerPoint=new THREE.Vector3(1.4,5,3.4);
 const ray=new THREE.Raycaster(),mouse=new THREE.Vector2(),pointer=new THREE.Vector2(),smoothed=new THREE.Vector2();
 const sharedRing=new THREE.MeshBasicMaterial({color:0xe6dcb8,transparent:true,opacity:.4,side:THREE.DoubleSide,depthWrite:false});
 function ui(){
  q('take-hand').hidden=state!=='idle';q('offer-hand').hidden=state!=='holding';q('hang-hand').hidden=state!=='holding';q('repeat-ritual').hidden=state!=='complete';
  q('continue-mountain').hidden=state!=='complete';
  q('return-river').disabled=state==='offering'||state==='growing';
  [...hud.querySelectorAll('.ritual-progress i')].forEach((e,i)=>e.classList.toggle('done',i<round));
 }
 function normalizeHand(source){
  const group=new THREE.Group(),mesh=source.clone(true);mesh.position.set(0,0,0);mesh.quaternion.identity();mesh.scale.set(1,1,1);group.add(mesh);
  const box=new THREE.Box3().setFromObject(mesh),center=box.getCenter(new THREE.Vector3());mesh.position.set(-center.x,-box.max.y,-center.z);
  group.scale.setScalar(1/(box.max.y-box.min.y));return group;
 }
 function load(){
  if(loadPromise)return loadPromise;
  loadPromise=new GLTFLoader().loadAsync('./models/jiuge_keeper.glb').then(g=>{
   model=g.scene;scene.add(model);const seen=new Set();model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;for(const m of [].concat(o.material)){if(seen.has(m))continue;seen.add(m);const tint=m.userData.web_color_multiplier;if(tint)m.color.multiply(new THREE.Color(...tint));m.roughness=Math.max(.68,m.roughness??.8);if(m.map)m.map.anisotropy=4;addHeightHaze(m);}}});
   keeper=model.getObjectByName('Keeper');
   for(let i=0;i<54;i++){const a=model.getObjectByName(`Branch_Anchor_${String(i).padStart(2,'0')}`);if(a)anchors.push(a.getWorldPosition(new THREE.Vector3()));}
   const tree=model.getObjectByName('Remembrance_Tree'),pivot=new THREE.Group();pivot.position.set(-5,1.4,3);scene.add(pivot);pivot.attach(tree);pivot.updateMatrixWorld(true);
   anchors.forEach(p=>pivot.worldToLocal(p));pivot.scale.set(1.27,1.15,1.18);pivot.updateMatrixWorld(true);anchors.forEach(p=>pivot.localToWorld(p));
   const candidates=[];tree.traverse(o=>{if(!o.isMesh)return;const attr=o.geometry.attributes.position;for(let i=0;i<attr.count;i+=Math.max(1,Math.floor(attr.count/5000))){const p=new THREE.Vector3().fromBufferAttribute(attr,i).applyMatrix4(o.matrixWorld);if(p.y>8.1)candidates.push(p);}});
   // Deterministic surface sampling fills the enlarged crown without floating hands.
   candidates.sort((a,b)=>Math.sin(a.x*37+a.y*19+a.z*13)-Math.sin(b.x*37+b.y*19+b.z*13));
   for(const p of candidates){if(anchors.every(q=>Math.hypot(p.x-q.x,(p.y-q.y)*1.15,(p.z-q.z)*.35)>.43))anchors.push(p);if(anchors.length>=150)break;}
   // Sort across the canopy so each completed offering awakens a distinct area.
   anchors.sort((a,b)=>a.x-b.x);
   if(anchors.length<3)throw new Error('Missing tree attachment points');
   const a=model.getObjectByName('Hand_Template_1'),b=model.getObjectByName('Hand_Template_2');
   if(!a||!b)throw new Error('Missing hand templates');
   const prototypes=[normalizeHand(a),normalizeHand(b)];a.visible=b.visible=false;
   anchors.forEach((p,i)=>{const h=prototypes[i%2].clone(true);h.position.copy(p);h.userData.size=.82+(i%5)*.06;h.userData.phase=i*2.399;h.traverse(o=>{if(o.isMesh)o.castShadow=false;});h.scale.setScalar(.001);h.visible=false;scene.add(h);hands.push(h);});
   pickup=prototypes[0].clone(true);pickup.scale.setScalar(1.25);pickup.position.copy(pickupStart);pickup.rotation.z=-.17;scene.add(pickup);
   halo=new THREE.Mesh(new THREE.RingGeometry(.72,.76,48),sharedRing);halo.position.copy(pickupStart).add(new THREE.Vector3(0,-.55,0));scene.add(halo);
   branchMarker=new THREE.Mesh(new THREE.SphereGeometry(.2,16,12),new THREE.MeshBasicMaterial({color:0xf0dfae,transparent:true,opacity:.65}));branchMarker.visible=false;scene.add(branchMarker);
   loaded=true;state='idle';ui();return true;
  }).catch(e=>{error=e;loadPromise=null;console.error('Chapter II:',e);return false;});
  return loadPromise;
 }
 function take(){if(!active||state!=='idle')return;state='holding';pickup.visible=false;halo.visible=false;line.textContent='A touch can become a memory.';hint.textContent='Offer it to the keeper, or choose the glowing branch.';branchMarker.position.copy(anchors[Math.min(round*Math.ceil(anchors.length/3)+4,anchors.length-1)]);branchMarker.visible=true;ui();}
 function choose(choice){
  if(state!=='holding')return;
  mode=choice;state='offering';anim=0;branchMarker.visible=false;offering=pickup.clone(true);offering.visible=true;offering.position.copy(pickupStart);scene.add(offering);
  line.textContent=choice==='keeper'?'He receives what words could not carry.':'Let this unfinished farewell find a place.';hint.textContent='';ui();
 }
 function reset(){round=0;state='idle';anim=0;hands.forEach(h=>{h.visible=false;h.scale.setScalar(.001);});if(offering){scene.remove(offering);offering=null;}pickup.visible=halo.visible=true;branchMarker.visible=false;line.textContent='Some farewells were left unfinished.';hint.textContent='Choose the pale hand by the water.';ui();}
 q('take-hand').onclick=take;q('offer-hand').onclick=()=>choose('keeper');q('hang-hand').onclick=()=>choose('tree');q('repeat-ritual').onclick=reset;
 const pick=(event)=>{
  if(!active||!loaded||!['idle','holding'].includes(state))return;
  const rect=renderer.domElement.getBoundingClientRect();mouse.set((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1);ray.setFromCamera(mouse,camera);
  if(state==='idle'&&ray.intersectObject(pickup,true).length)take();
  else if(state==='holding'){if(ray.intersectObject(branchMarker,true).length||ray.intersectObject(scene.getObjectByName('Remembrance_Tree'),true).length)choose('tree');else if(ray.intersectObject(keeper,true).length)choose('keeper');}
 };
 renderer.domElement.addEventListener('click',pick);
 function update(dt,time,look){
  if(!active)return;pointer.copy(look);smoothed.lerp(pointer,1-Math.exp(-dt*2));
  camera.aspect=renderer.domElement.clientWidth/renderer.domElement.clientHeight;camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(31))/camera.aspect));camera.updateProjectionMatrix();
  chapterTime+=dt;const orbit=.22+Math.sin(chapterTime*.12)*.09+smoothed.x*.10;
  camera.position.set(1+Math.sin(orbit)*40,10.7+Math.sin(chapterTime*.09)*.45-smoothed.y*.4,-1+Math.cos(orbit)*40);
  camera.lookAt(1-round*.45,7.8+round*.2-smoothed.y*.55,-1);atmosphere.update(time);
  if(!loaded)return;
  if(halo.visible){halo.quaternion.copy(camera.quaternion);halo.material.opacity=.25+Math.sin(time*2)*.13;pickup.position.y=pickupStart.y+Math.sin(time)*.09;}
  if(branchMarker.visible)branchMarker.scale.setScalar(1+Math.sin(time*2)*.15);
  if(state==='offering'){
   anim+=dt;const t=Math.min(anim/3.4,1),target=anchors[Math.min(round*Math.ceil(anchors.length/3)+4,anchors.length-1)];
   if(mode==='keeper'&&t<.5){offering.position.lerpVectors(pickupStart,offerPoint,t*2);offering.position.y+=Math.sin(t*Math.PI*2)*1.5;}
   else{const start=mode==='keeper'?offerPoint:pickupStart,u=mode==='keeper'?(t-.5)*2:t;offering.position.lerpVectors(start,target,u);offering.position.y+=Math.sin(u*Math.PI)*2;}
   offering.rotation.y+=dt*.3;keeperLight.intensity=mode==='keeper'?Math.sin(t*Math.PI)*18:0;
   if(t>=1){scene.remove(offering);offering=null;state='growing';anim=0;}
  }
  if(state==='growing'){
   anim+=dt;const batch=Math.ceil(hands.length/3),start=round*batch,end=Math.min(start+batch,hands.length);
   for(let i=start;i<end;i++){const h=hands[i],p=THREE.MathUtils.smoothstep(anim-(i-start)*1.8/batch,0,1.1);h.visible=p>0;h.scale.setScalar(Math.max(.001,p*h.userData.size));}
   keeperLight.intensity=Math.max(0,keeperLight.intensity-dt*8);
   if(anim>3.3){round++;state=round===3?'complete':'idle';pickup.visible=halo.visible=state==='idle';line.textContent=round===3?'What could not reach home is remembered here.':round===1?'One memory awakens another.':'There is room for one more farewell.';hint.textContent=round===3?'Stay a moment. The river will carry us onward.':'Choose another hand by the water.';ui();if(round===3)window.dispatchEvent(new CustomEvent('jiuge:chapter-complete',{detail:{chapter:2,nextChapter:3}}));}
  }
  hands.forEach(h=>{if(h.visible){h.rotation.z=Math.sin(time*.65+h.userData.phase)*.035;h.rotation.x=Math.cos(time*.45+h.userData.phase)*.025;}});
  renderer.domElement.dataset.chapter='2';renderer.domElement.dataset.ritualState=state;renderer.domElement.dataset.offerings=String(round);
  renderer.domElement.dataset.hangingHands=String(hands.length);
 }
 return {scene,camera,load,get loaded(){return loaded;},get error(){return error;},get active(){return active;},
  enter(preserve=false){active=true;chapterTime=0;hud.hidden=false;water.position.y=0;scene.add(water);if(!preserve)reset();},
  leave(){active=false;hud.hidden=true;},update,
  onReturn(callback){q('return-river').onclick=callback;},onContinue(callback){q('continue-mountain').onclick=callback;}
 };
}
