# Pixel Water UE 5.7 migration

This branch is the UE 5.7 migration workspace for the original Unity 2D pixel water shader.

## What is included

- `PixelWaterUE57.uproject` — project descriptor for UE 5.7
- `Config/*.ini` — initialization and editor settings
- `Content/Water/WaterPixelShader_CustomNode.hlsl` — shader reference for a Material Custom node
- `Content/Water/UE5_Migration.md` — migration guide
- `Tools/import_textures.py` — Python helper to import the original PNGs into `/Game/SourceTextures/`
- `Source/*.Target.cs` and `Source/PixelWaterUE57/*` — minimal C++ target/module stubs so the project is a standard UE project skeleton

## Important note

This repository can provide the project shell and migration reference, but UE binary assets such as `.uasset`, Material assets, Level maps, Paper2D tile assets, and Niagara particles still need to be created in the Unreal Editor. Unity `.unity`, `.shadergraph`, `.mat`, Tilemap and Prefab assets cannot be imported as-is into UE.

## Open in UE 5.7

1. Install UE 5.7.
2. Open `PixelWaterUE57.uproject`.
3. Let Unreal generate the project files if prompted.
4. Import the original PNG textures from `Assets/` (or use `Tools/import_textures.py` from the editor Python console).
5. Create `M_WaterPixel`, wire the Custom node, and rebuild the 2D scene in a new level.

## Fidelity note

The shader is a careful manual approximation of the original Unity Shader Graph, not an automated conversion. The original project does not include the heightmap generation code, so the foam edge and terrain influence cannot be reproduced exactly without the missing source data.
