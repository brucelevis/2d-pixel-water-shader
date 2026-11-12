# Unreal Engine 5.7 migration workspace

This branch adds an Unreal Engine 5.7 project entry point and migration tooling while preserving the original Unity project under `Assets/`. The Unity source is a URP/Shader Graph 2D scene; Unity `.unity`, `.mat`, `.shadergraph`, Tilemap, and Prefab files are not Unreal assets and cannot be converted into valid `.uasset` files by changing their extensions.

## Open

1. Install UE 5.7 and open `PixelWaterUE57.uproject`.
2. Allow Unreal to generate project files/assets as needed. This is an editor project, not a prebuilt game.
3. In the Unreal Editor, run `Tools/import_textures.py` with the Python console (Window → Developer Tools → Output Log, then enter `py "<absolute path to this repo>/Tools/import_textures.py"`). The script imports original PNG files from `Assets/` into `/Game/SourceTextures/`, sets nearest filtering and disables mipmaps, and saves the imported textures.
4. Follow `Content/Water/UE5_Migration.md` to create the UE material and reconstruct the scene.

## Migration status / fidelity

The project descriptor, baseline config, texture import automation, and a UE Custom Material HLSL reference are provided. This is **not yet a one-to-one reproduction**: Unreal binary assets (material, level, Paper2D tile assets and particle system) must be created/saved in UE Editor, and visual equivalence must be tested there. The upstream README explicitly says the heightmap-generation code is not included, so heightmap-driven foam cannot be reconstructed exactly from this repository alone. The Custom-node shader is a documented approximation of the Unity Shader Graph, not an automatic graph conversion.

## Original project

The existing Unity project remains available and can still be opened with Unity 2022.3.6f1. See `Assets/` and the original source README for details.
