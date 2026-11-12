# UE 5.7 手动迁移步骤

## 已知限制

原仓库是 Unity 2022.3.6f1 的 URP/Shader Graph 示例。UE 不会读取 Unity 的 `.unity` 场景、`.shadergraph`、`.mat`、Tilemap 或 Prefab 文件作为可编辑资产。UE 的 Material、Level、TileSet、TileMap 等需要在编辑器里创建并保存为 UE `.uasset`。原 README 也明确指出未提供高度图生成代码。因此，仅靠仓库中的现有源文件不能保证严格一比一重建；需要编辑器内创建资产并用目标平台实机对比调参。

## 贴图导入

先打开根目录的 `PixelWaterUE57.uproject`，然后在编辑器 Output Log 的 Python Console 执行 `Tools/import_textures.py`。脚本扫描原始 `Assets/` 目录里的 PNG 并导入到 `/Game/SourceTextures/`，采用 Nearest 过滤和 NoMipmaps。若 `Texture2D` 属性在具体 UE 5.7 安装中名称有差异，手动在纹理资产中设置 Filter=Nearest、Mip Gen Settings=NoMipmaps，并保存。

## 水面材质参考

新建 `M_WaterPixel` 材质：Surface / Translucent / Unlit。建立 Custom 节点，Output Type 选择 Float4，代码复制自 `Content/Water/WaterPixelShader_CustomNode.hlsl`。创建以下输入 pin（名称大小写必须一致）：

| Pin | 类型 | 起始值/连接 |
| --- | --- | --- |
| UV | Float2 | TextureCoordinate |
| WorldPosition | Float3 | AbsoluteWorldPosition |
| Time | Float | Time |
| PixelGrid | Float2 | (320, 180)，按目标像素分辨率调整 |
| WorldTextureScale | Float | 0.005681818 |
| WorldTextureOffset | Float2 | (0, 0) |
| CausticScale / CausticSpeed | Float | 0.08 / 0.8 |
| CausticMovementAmount / CausticFaderScale | Float | 0.018 / 0.17 |
| CausticThreshold / CausticHighlightStrength | Float | 0 / 0.3686，按贴图调整 |
| CausticTexture / CausticTextureSampler | Texture2D / SamplerState | CausticTexture.png 与 Texture Sampler |
| CausticHighlightTexture / CausticHighlightSampler | Texture2D / SamplerState | CausticTextureHighlights.png 与 Texture Sampler |
| FoamTexture / FoamTextureSampler | Texture2D / SamplerState | Water.png 或匹配泡沫遮罩的纹理 |
| FoamScale / FoamBlur | Float | 0.16 / 5 |
| FoamTexelSize | Float2 | (1/贴图宽, 1/贴图高) |
| MainColour | Float4 | (0.24252, 0.51713, 0.645, 0.52549) |
| CausticColour | Float4 | (0.45490, 0.77255, 0.76471, 0.12157) |
| FoamColour | Float4 | (1, 1, 1, 1) |
| SpecularColour | Float4 | (1, 1, 1, 0.87059) |
| SpecularScale / SpecularScale2 | Float | 0.83 / 3.68 |
| SpecularSpeed / SpecularThreshold | Float | 0.3 / -0.84 |

Custom 输出 Float4 可用 ComponentMask 分离：RGB 接 Emissive Color，A 接 Opacity。设置材质 Two Sided 与透明排序需依场景测试。把材质赋给 XY 平面的网格或 Paper2D Sprite。

代码里 3×3 固定盒式模糊只近似 Unity GaussianBlur 子图，采样通道、UV、世界坐标映射与透明混合均需通过 UE 预览校准。UE Custom 节点是参考实现，不是 Shader Graph 的逐节点翻译。

## 关卡重建

依据 `Assets/Scenes/SampleScene.unity` 在 UE 中新建关卡：使用正交相机，重建水面 Tilemap 与沙滩 Sprite 层级；可用 Paper2D TileSet/TileMap 或平面网格组织贴图。Unity 粒子 Prefab 需在 UE 中用 Niagara 重做。创建完毕后手动保存 UE 资产并设置 Game Default Map。

若要求视觉一比一，必须在 UE 5.7 中对照 Unity 原场景逐项验证：镜头画幅/位置、贴图切片与 tile 坐标、混合/排序、像素采样、Shader 参数、泡沫高度图及粒子。由于高度图算法未随上游提供，此处无法声称或验证像素级一致。
