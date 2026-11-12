import os
import unreal

"""Run from the UE 5.7 Editor Python console after opening PixelWaterUE57.uproject.

Imports the repository's PNGs, creates M_WaterPixel and M_Sand, then creates a
basic orthographic preview level with water and sand planes. This deliberately
creates native UE assets in-editor; it does not pretend Unity YAML/ShaderGraph
files are UE .uasset files.
"""

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PNG_ROOT = os.path.join(ROOT, "Assets")
CONTENT_ROOT = "/Game/PixelWater"
TEXTURE_ROOT = CONTENT_ROOT + "/Textures"
MATERIAL_ROOT = CONTENT_ROOT + "/Materials"
MAP_ROOT = CONTENT_ROOT + "/Maps"


def log(message):
    unreal.log("[PixelWaterUE57] " + message)


def ensure_directory(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def import_textures():
    ensure_directory(TEXTURE_ROOT)
    imported = {}
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    for current, _, files in os.walk(PNG_ROOT):
        for filename in files:
            if not filename.lower().endswith(".png"):
                continue
            source = os.path.join(current, filename)
            rel = os.path.relpath(current, PNG_ROOT).replace("\\", "/")
            destination = TEXTURE_ROOT if rel == "." else TEXTURE_ROOT + "/" + rel
            ensure_directory(destination)
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", source)
            task.set_editor_property("destination_path", destination)
            task.set_editor_property("automated", True)
            task.set_editor_property("replace_existing", True)
            task.set_editor_property("save", True)
            tools.import_asset_tasks([task])
            for path in task.get_editor_property("imported_object_paths"):
                asset = unreal.load_asset(path)
                if isinstance(asset, unreal.Texture2D):
                    asset.set_editor_property("filter", unreal.TextureFilter.NEAREST)
                    asset.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
                    unreal.EditorAssetLibrary.save_loaded_asset(asset)
                    imported[os.path.basename(source)] = asset
    log("Imported {} PNG textures.".format(len(imported)))
    return imported


def make_asset(name, path, asset_class, factory):
    existing = unreal.EditorAssetLibrary.load_asset(path + "/" + name)
    if existing:
        unreal.EditorAssetLibrary.delete_asset(path + "/" + name)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, path, asset_class, factory)


def add_custom_pin(custom, name):
    # FCustomInput is exposed by UE Python as unreal.CustomInput in UE 5.7.
    pin = unreal.CustomInput()
    pin.set_editor_property("input_name", name)
    return pin


def create_water_material(textures):
    ensure_directory(MATERIAL_ROOT)
    material = make_asset("M_WaterPixel", MATERIAL_ROOT, unreal.Material, unreal.MaterialFactoryNew())
    if not material:
        raise RuntimeError("Could not create M_WaterPixel")
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)

    code_path = os.path.join(ROOT, "Content", "Water", "WaterPixelShader_CustomNode.hlsl")
    with open(code_path, "r", encoding="utf-8") as source:
        code = source.read()
    custom = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionCustom, -500, 0)
    custom.set_editor_property("code", code)
    custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)

    pin_names = [
        "UV", "WorldPosition", "Time", "PixelGrid", "WorldTextureScale", "WorldTextureOffset",
        "CausticScale", "CausticSpeed", "CausticMovementAmount", "CausticFaderScale",
        "CausticThreshold", "CausticHighlightStrength", "CausticTexture", "CausticHighlightTexture",
        "FoamTexture", "FoamScale", "FoamBlur", "FoamTexelSize", "MainColour", "CausticColour",
        "FoamColour", "SpecularColour", "SpecularScale", "SpecularScale2", "SpecularSpeed",
        "SpecularThreshold"
    ]
    custom.set_editor_property("inputs", [add_custom_pin(name) for name in pin_names])

    def expr(cls, x, y):
        return unreal.MaterialEditingLibrary.create_material_expression(material, cls, x, y)

    def connect(node, output_index, input_name):
        ok = unreal.MaterialEditingLibrary.connect donner if False else True
        # connect_material_expressions(source, output_name, destination, input_name)
        result = unreal.MaterialEditingLibrary.connect_material_expressions(node, "", custom, input_name)
        if result is False:
            raise RuntimeError("Failed wiring {} into Custom input {}".format(node.get_name(), input_name))

    uv = expr(unreal.MaterialExpressionTextureCoordinate, -900, -450)
    world = expr(unreal.MaterialExpressionWorldPosition, -900, -350)
    world.set_editor_property("world_position", unreal.MaterialPositionWS.ABSOLUTE)
    time_node = expr(unreal.MaterialExpressionTime, -900, -250)
    connect(uv, 0, "UV")
    connect(world, 0, "WorldPosition")
    connect(time_node, 0, "Time")

    constants = {
        "PixelGrid": (unreal.MaterialExpressionConstant2Vector, (320.0, 180.0)),
        "WorldTextureScale": (unreal.MaterialExpressionConstant, (0.005681818,)),
        "WorldTextureOffset": (unreal.MaterialExpressionConstant2Vector, (0.0, 0.0)),
        "CausticScale": (unreal.MaterialExpressionConstant, (0.08,)),
        "CausticSpeed": (unreal.MaterialExpressionConstant, (0.8,)),
        "CausticMovementAmount": (unreal.MaterialExpressionConstant, (0.018,)),
        "CausticFaderScale": (unreal.MaterialExpressionConstant, (0.17,)),
        "CausticThreshold": (unreal.MaterialExpressionConstant, (0.0,)),
        "CausticHighlightStrength": (unreal.MaterialExpressionConstant, (0.36862746,)),
        "FoamScale": (unreal.MaterialExpressionConstant, (0.16,)),
        "FoamBlur": (unreal.MaterialExpressionConstant, (5.0,)),
        "FoamTexelSize": (unreal.MaterialExpressionConstant2Vector, (0.005, 0.005)),
        "MainColour": (unreal.MaterialExpressionConstant4Vector, (0.24251999, 0.5171283, 0.645, 0.5254902)),
        "CausticColour": (unreal.MaterialExpressionConstant4Vector, (0.45490196, 0.77254903, 0.7647059, 0.12156863)),
        "FoamColour": (unreal.MaterialExpressionConstant4Vector, (1.0, 1.0, 1.0, 1.0)),
        "SpecularColour": (unreal.MaterialExpressionConstant4Vector, (1.0, 1.0, 1.0, 0.87058824)),
        "SpecularScale": (unreal.MaterialExpressionConstant, (0.83,)),
        "SpecularScale2": (unreal.MaterialExpressionConstant, (3.68,)),
        "SpecularSpeed": (unreal.MaterialExpressionConstant, (0.3,)),
        "SpecularThreshold": (unreal.MaterialExpressionConstant, (-0.84,))
    }
    for index, (name, (cls, values)) in enumerate(constants.items()):
        node = expr(cls, -1100, -100 + index * 90)
        props = ["r", "g", "b", "a"] if cls == unreal.MaterialExpressionConstant4Vector else (["r", "g"] if cls == unreal.MaterialExpressionConstant2Vector else ["r"])
        for prop, value in zip(props, values):
            node.set_editor_property(prop, value)
        connect(node, 0, name)

    texture_pins = {
        "CausticTexture": "CausticTexture.png",
        "CausticHighlightTexture": "CausticTextureHighlights.png",
        "FoamTexture": "Water.png"
    }
    for index, (pin_name, filename) in enumerate(texture_pins.items()):
        texture = textures.get(filename)
        if not texture:
            log("Texture missing for {}: {}".format(pin_name, filename))
            continue
        node = expr(unreal.MaterialExpressionTextureObject, -900, 600 + index * 130)
        node.set_editor_property("texture", texture)
        connect(node, 0, pin_name)

    rgb = expr(unreal.MaterialExpressionComponentMask, 150, 0)
    rgb.set_editor_property("r", True)
    rgb.set_editor_property("g", True)
    rgb.set_editor_property("b", True)
    alpha = expr(unreal.MaterialExpressionComponentMask, 150, 180)
    alpha.set_editor_property("a", True)
    unreal.MaterialEditingLibrary.connect_material_expressions(custom, "", rgb, "Input")
    unreal.MaterialEditingLibrary.connect_material_expressions(custom, "", alpha, "Input")
    unreal.MaterialEditingLibrary.connect_material_property(rgb, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(alpha, unreal.MaterialProperty.MP_OPACITY)
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    log("Created M_WaterPixel. Check the material compiler log and adjust if UE 5.7 Python API differs.")
    return material


def create_sand_material(textures):
    texture = textures.get("BeachSandTexture.png")
    if not texture:
        log("BeachSandTexture.png missing; skipping M_Sand")
        return None
    material = make_asset("M_Sand", MATERIAL_ROOT, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    sample = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionTextureSample, -250, 0)
    sample.set_editor_property("texture", texture)
    unreal.MaterialEditingLibrary.connect_material_property(sample, unreal.MaterialProperty.MP_EMISSIVE_COLOR, "RGB")
    unreal.MaterialEditingLibrary.connect_material_property(sample, unreal.MaterialProperty.MP_OPACITY, "A")
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


def create_preview_level(water_material, sand_material):
    ensure_directory(MAP_ROOT)
    map_path = MAP_ROOT + "/L_PixelWaterPreview"
    if unreal.EditorAssetLibrary.does_asset_exist(map_path):
        unreal.EditorAssetLibrary.delete_asset(map_path)
    unreal.EditorLevelLibrary.new_level(map_path)

    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    if not plane:
        log("Engine plane mesh unavailable; create two XY planes manually in the level.")
        return
    sand_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
    sand_actor.static_mesh_component.set_static_mesh(plane)
    sand_actor.static_mesh_component.set_material(0, sand_material)
    sand_actor.set_actor_scale3d(unreal.Vector(20, 20, 1))

    water_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 5))
    water_actor.static_mesh_component.set_static_mesh(plane)
    water_actor.static_mesh_component.set_material(0, water_material)
    water_actor.set_actor_scale3d(unreal.Vector(18, 18, 1))

    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0, 0, 1800))
    camera.set_actor_rotation(unreal.Rotator(-90, 0, 0), False)
    camera.camera_component.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
    camera.camera_component.set_editor_property("ortho_width", 2200.0)
    unreal.EditorLevelLibrary.save_current_level()
    log("Created preview level: {}".format(map_path))


def run():
    for folder in (CONTENT_ROOT, TEXTURE_ROOT, MATERIAL_ROOT, MAP_ROOT):
        ensure_directory(folder)
    textures = import_textures()
    water = create_water_material(textures)
    sand = create_sand_material(textures)
    create_preview_level(water, sand)
    log("Setup complete. Open /Game/PixelWater/Maps/L_PixelWaterPreview and inspect shader/material errors.")


run()
