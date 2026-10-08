import * as THREE from 'three';

// Soft, depth-tested atmospheric layers; no external textures or postprocessing.
export function createAtmosphere(scene) {
  const time = { value: 0 };
  const noise = `
    float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
    float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*noise(p);p=p*2.03+7.1;a*=.5;}return v;}
  `;
  const sky = new THREE.Mesh(new THREE.SphereGeometry(650,32,20),new THREE.ShaderMaterial({
    side:THREE.BackSide,depthWrite:false,uniforms:{uTime:time},
    vertexShader:`varying vec3 vDirection;void main(){vDirection=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`varying vec3 vDirection;uniform float uTime;${noise}
      void main(){vec3 d=normalize(vDirection);float elevation=smoothstep(-.08,.8,d.y);
        vec3 col=mix(vec3(.44,.56,.59),vec3(.22,.35,.40),elevation);
        float cloud=fbm(d.xz*4.5/(.5+max(d.y,0.))+vec2(uTime*.001,0.));
        col=mix(col,vec3(.68,.74,.73),smoothstep(.28,.8,cloud)*.6);
        float glow=pow(max(dot(d,normalize(vec3(.18,.65,-1.))),0.),9.);
        col+=vec3(.50,.47,.36)*glow;
        gl_FragColor=vec4(col,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`
  }));sky.renderOrder=-10;scene.add(sky);

  const layers=[];
  for(let i=0;i<7;i++){
    const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,
      uniforms:{uTime:time,uSeed:{value:i*9.7},uOpacity:{value:i<2?.16:.23}},
      vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
      fragmentShader:`varying vec2 vUv;uniform float uTime,uSeed,uOpacity;${noise}
        void main(){vec2 p=vUv;float edge=smoothstep(0.,.18,p.x)*smoothstep(0.,.18,1.-p.x);
          float vertical=pow(max(sin(p.y*3.14159265),0.),2.);
          float wisps=fbm(vec2(p.x*7.+uTime*.018+uSeed,p.y*2.7));
          float a=edge*vertical*smoothstep(.15,.75,wisps)*uOpacity;
          gl_FragColor=vec4(.64,.74,.75,a);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }`
    });
    const layer=new THREE.Mesh(new THREE.PlaneGeometry(100+i*13,6+i*.9),material);
    layer.position.set(i%2?7:-7,1.4+i*.3,4-i*21);scene.add(layer);layers.push(layer);
  }
  // Light shafts are soft transparent volumes, an inexpensive approximation.
  for(let i=0;i<3;i++){
    const beam=new THREE.Mesh(new THREE.CylinderGeometry(2.3,10+i*2,100,24,1,true),new THREE.ShaderMaterial({
      transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,
      uniforms:{uStrength:{value:.028-i*.005}},
      vertexShader:`varying vec2 vUv;varying vec3 vNormal,vView;void main(){vUv=uv;vec4 p=modelViewMatrix*vec4(position,1.);vView=-p.xyz;vNormal=normalMatrix*normal;gl_Position=projectionMatrix*p;}`,
      fragmentShader:`varying vec2 vUv;varying vec3 vNormal,vView;uniform float uStrength;
        void main(){float facing=pow(abs(dot(normalize(vNormal),normalize(vView))),1.5);
          float fade=smoothstep(0.,.22,vUv.y)*smoothstep(0.,.3,1.-vUv.y);
          gl_FragColor=vec4(.74,.80,.75,uStrength*facing*fade);}`
    }));beam.position.set(6+i*11,43,-65-i*29);beam.rotation.z=-.23;beam.rotation.x=.12;scene.add(beam);
  }
  return { update(seconds){time.value=seconds;layers.forEach((l,i)=>{l.position.x=(i%2?7:-7)+Math.sin(seconds*.025+i)*2;});} };
}

export function addHeightHaze(material){
  material.onBeforeCompile=shader=>{
    shader.vertexShader='varying vec3 vHazeWorld;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\nvHazeWorld=(modelMatrix*vec4(transformed,1.)).xyz;');
    shader.fragmentShader='varying vec3 vHazeWorld;\n'+shader.fragmentShader;
    shader.fragmentShader=shader.fragmentShader.replace('#include <fog_fragment>',`#include <fog_fragment>
      float lowMist=exp(-max(vHazeWorld.y,0.)*.24)*(1.-exp(-length(cameraPosition-vHazeWorld)*.008));
      gl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(.57,.67,.68),lowMist*.42);`);
  };
  material.customProgramCacheKey=()=> 'jiuge-height-haze-v1';
}
