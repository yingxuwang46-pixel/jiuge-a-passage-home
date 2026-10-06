# A Passage Home | 九歌·归渡

**A world for those who cannot return home.**
A passage across distance, time, and loss, inspired by ancient Chu ritual poetry.

[Play the five-chapter demo](https://jiuge-a-passage-home.wyx1219.chatgpt.site) · [Download project files](https://github.com/yingxuwang46-pixel/jiuge-a-passage-home/releases/latest)

## Downloads / 工程下载

Open **Releases** and download:

- **jiuge-web-demo-v1.0.0.zip** — complete runnable website, all five GLB scene models, local Three.js runtime and editable source.
- **jiuge-blender-projects-v1.0.0.zip** — five editable Blender scene files with packed textures.
- **SHA256SUMS.txt** — checksums for the two downloads.

GitHub's automatic Source code ZIP contains the text source in this repository. Download the named release ZIPs above for the full 3D assets.

## Run locally

Extract the web demo ZIP, open a terminal in its top-level folder, and run:

```sh
python3 -m http.server 8765
```

Open http://localhost:8765/web/ in a desktop browser with WebGL enabled. Do not open index.html directly with file://. No build step, API key or account is required.

## Source map

- `web/scene.js`: renderer, first chapter and chapter transitions.
- `web/keeper.js`, `mountain.js`, `ritual.js`, `finale.js`: chapters II–V.
- `web/atmosphere.js`, `mountain-atmosphere.js`: atmospheric effects.
- Root Python scripts: Blender assembly and model preparation pipeline.
- [Project guide](PROJECT.md): controls, Blender versions and pipeline notes.

## 操作

适合电脑浏览器。按英文按钮推进各幕；终章点击三个不同的大红花，水面荡漾后红色花瓣伞逐渐长出。可拖动观察、返回上一幕或从头重玩。

Public repository for viewing and downloading the competition project. No additional license to the original artwork is granted. Third-party software retains its own license.
