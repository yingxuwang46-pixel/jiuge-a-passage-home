# Project guide

Five-chapter desktop-browser artwork inspired by the imagery of ancient Chu ritual poetry.

1. River crossing: a bird-headed boat turns into the canyon; an eye in the stone palm follows it.
2. Keeper: offer a white hand or hang it on the tree; three offerings fill the branches.
3. Mountain: a cloth-wrapped figure and leopard beneath an ancient tree; butterflies carry the interaction.
4. Ritual: approach the procession and awaken a golden glow on the drum surface.
5. Finale: touch three distinct flowers, release ripples, and grow a red petal canopy from the empty white robe.

The interface is English; the Chinese title is retained. This is a poetic interactive artwork, not a historical reconstruction.

## Editable Blender projects

- jiuge_canyon_v02.blend
- jiuge_keeper_v01.blend
- jiuge_mountain_v02.blend
- jiuge_ritual_v03.blend
- jiuge_finale_v01.blend

Created using Blender 5.2.2. Textures are packed. In the finale, frame 1 is the initial state, frame 180 shows the bloom, and frame 270 shows the ending camera. Web interaction and some camera/instance adjustments run in JavaScript; Blender timelines are editable visual demonstrations, not clickable gameplay.

## Pipeline

The Python scripts are retained for reference and regeneration. Run them from the project root. Blender scripts need Blender's Python environment; image-compression scripts need Pillow. Regeneration from the beginning additionally needs the original Tripo exports in source-assets/assets, assets02, assets03, assets04 and assets05. Those original source exports are not included in these releases. The packed .blend files can be opened without regenerating them.

## Credits and rights

Concept, scene direction and reference selection: Yingxu Wang. Models generated with Tripo3D; assembly in Blender; real-time implementation with Three.js and AI-assisted development. Three.js is distributed under its included MIT license. Public download does not automatically grant a license to reuse the artwork.
