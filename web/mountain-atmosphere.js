import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
// Local drifting veils leave open windows between peaks instead of bleaching the whole valley.
export function mountainMist(scene){
 const clock={value:0},layers=[];
 const noise=`float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*noise(p);p=p*2.07+3.8;a*=.5;}return v;}`;
 for(let i=0;i<12;i++){
  const m=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,uniforms:{uTime:clock,uSeed:{value:i*13.1},uAlpha:{value:i<4?.23:.38}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:`varying vec2 vUv;uniform float uTime,uSeed,uAlpha;${noise}void main(){vec2 p=vUv;float edge=smoothstep(0.,.23,p.x)*smoothstep(0.,.23,1.-p.x)*pow(sin(p.y*3.14159265),2.);float n=fbm(vec2(p.x*5.-uTime*.016+uSeed,p.y*3.+sin(uTime*.035+uSeed)*.3));float a=edge*smoothstep(.26,.68,n)*uAlpha;vec3 c=mix(vec3(.40,.52,.55),vec3(.68,.76,.76),n);gl_FragColor=vec4(c,a);#include <tonemapping_fragment>\n#include <colorspace_fragment>}`.replace(';#include',';\n#include')});
  const o=new THREE.Mesh(new THREE.PlaneGeometry(65+i*5,12+i%4*5),m);o.position.set(12+(i%3)*12,-12+(i%4)*8,-22-i*10);o.rotation.z=(i%3-1)*.08;o.userData.x=o.position.x;scene.add(o);layers.push(o);
 }
 return {update(t){clock.value=t;layers.forEach((o,i)=>o.position.x=o.userData.x+Math.sin(t*.027+i)*3);}};
}
export function addMountainVegetation(model,scene){
 const points=[],normal=new THREE.Vector3(),p=new THREE.Vector3();model.updateMatrixWorld(true);
 model.traverse(o=>{if(!o.isMesh||!/^Mountain_(Peak|Wall)/.test(o.name))return;const pos=o.geometry.attributes.position,norm=o.geometry.attributes.normal;if(!norm)return;const box=new THREE.Box3().setFromObject(o),nm=new THREE.Matrix3().getNormalMatrix(o.matrixWorld);const stride=Math.max(1,Math.floor(pos.count/2200));
  for(let i=0;i<pos.count;i+=stride){p.fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld);normal.fromBufferAttribute(norm,i).applyMatrix3(nm).normalize();const seed=Math.abs(Math.sin(i*12.989+p.x*7.1)*43758.5)%1;if(normal.y>.38&&p.y>Math.max(-4,box.max.y-40)&&seed>.38&&points.every(q=>q.distanceToSquared(p)>.45)){points.push(p.clone());if(points.length>=850)return;}}
 });
 const tufts=[];for(let j=0;j<5;j++){const g=new THREE.IcosahedronGeometry(.5,1),a=g.attributes.position;for(let v=0;v<a.count;v++){const r=.8+.25*Math.sin(v*37+j*19);a.setXYZ(v,a.getX(v)*r,a.getY(v)*r,a.getZ(v)*r);}g.translate(Math.sin(j*2.4)*.45,j%2*.2,Math.cos(j*2.4)*.4);g.computeVertexNormals();tufts.push(g);}
 const foliage=new THREE.InstancedMesh(mergeGeometries(tufts),new THREE.MeshStandardMaterial({color:0x263d31,roughness:1}),points.length),dummy=new THREE.Object3D();foliage.name='Cliff_Scrub';foliage.receiveShadow=true;
 points.forEach((p,i)=>{const r=.14+(Math.sin(i*17.3)*.5+.5)*.24;dummy.position.copy(p).add(new THREE.Vector3(0,r*.3,0));dummy.scale.set(r*1.3,r*.65,r);dummy.rotation.set(i*.3,i*2.4,0);dummy.updateMatrix();foliage.setMatrixAt(i,dummy.matrix);foliage.setColorAt(i,new THREE.Color().setRGB(.065+i%4*.012,.095+i%5*.009,.065+i%3*.01));});scene.add(foliage);
}
