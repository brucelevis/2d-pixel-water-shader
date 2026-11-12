import os
import unreal

# Run inside the Unreal Editor Python console. This script uses the original PNGs
# from the repository's Assets folder and imports them to /Game/SourceTextures.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
source_root = os.path.join(repo_root, "Assets")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

imported = []
for current_dir, _, filenames in os.walk(source_root):
    for filename in filenames:
        if not filename.lower().endswith(".png"):
            continue
        source_file = os.path.join(current_dir, filename)
        relative_dir = os.path.relpath(current_dir, source_root).replace("\\", "/")
        destination = "/Game/SourceTextures"
        if relative_dir != ".":
            destination += "/" + relative_dir

        task = unreal.AssetImportTask()
        task.filename = source_file
        task.destination_path = destination
        task.automated = True
        task.replace_existing = True
        task.save = True
        asset_tools.import_asset_tasks([task])

        for object_path in task.get_editor_property("imported_object_paths"):
            texture = unreal.load_asset(object_path)
            if isinstance(texture, unreal.Texture2D):
                texture.set_editor_property("filter", unreal.TextureFilter.NEAREST)
                texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
                texture.set_editor_property("s RGB", True)
                unreal.EditorAssetLibrary.save_loaded_asset(texture)
                imported.append(object_path)

unreal.log("Pixel Water UE5.7: imported and configured {} PNG textures.".format(len(imported)))
