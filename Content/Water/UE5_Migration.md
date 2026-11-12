# UE 5.7 手动迁移与自动生成

原仓库是 Unity 2022.3.6f1 URP/Shader Graph 2D 工程。Unity 的 `.unity` 场景、`.shadergraph`、`.mat`、Tilemap 和 Prefab 不是 UE 可直接加载的资产格式。项目里的脚本会在 Unreal Editor 中尝试创建原生资产，但不能在 GitHub 上直接生成或验证 UE 二进制 `.uasset`。

## 自动创建预览资产

1. 使用 UE 5.7 打开根目录 `PixelWaterUE57.uproject`。
2. 确认启用 Python Editor Script Plugin（若项目首次运行没有 Python Console，则到 Plugins 搜索启用并重启编辑器）。
3. 打开 Window → Developer Tools → Output Log，执行：`py "<仓库绝对路径>/Tools/build_ue_project.py"`。
4. 脚本会把 PNG 导入 `/Game/PixelWater/Textures/`，尝试创建 `M_WaterPixel`、`M_Sand`，并在 `/Game/PixelWater/Maps/L_PixelWaterPreview` 创建正交相机和平面预览关卡。
5. 检查 Output Log 和材质编译结果；若当前 UE 5.7 Python 暴露 API 或 Custom HLSL 纹理采样编译失败，按错误修正节点/纹理采样输入。保存后的 `.uasset` 位于项目 `Content/` 下，应在 UE 中打开确认后再提交。

脚本生成的预览关卡仅为起点，不代表已通过 UE 编辑器验证或达到像素级一致。具体效果要和 Unity 示例逐项对照调参。

## 材质算法与参数

`WaterPixelShader_CustomNode.hlsl` 是 UE Custom 节点参考，按其代码创建 Custom 节点，Output Type 为 Float4。代码基于原材质给出的主要数值实现像素化 UV、双层 caustics、泡沫纹理 3×3 盒式模糊和程序化高光。UV、透明模式、Sampler State、Gamma 与贴图通道必须在 UE 5.7 中实际预览校正。它不是 Unity Shader Graph 的等价逐节点反编译。

初始值来源于原始 Unity material：主水色 `(0.24252, 0.51713, 0.645, 0.52549)`、Caustic 色 `(0.45490, 0.77255, 0.76471, 0.12157)`、Caustic scale/speed `0.08/0.8`、foam scale `0.16`、specular scale `0.83/3.68`、speed `0.3`、threshold `-0.84`。

## 还原差异

原场景使用 Tilemap、沙滩 Sprite、正交相机、URP 2D 光照和粒子 Prefab。预览脚本用平面代替 Tilemap，用 Unlit 材质代替 Unity 2D Light，粒子仍须用 Niagara 重建。上游 README 明确写明高度图生成代码未包含；因此高度图驱动泡沫效果无法单靠当前仓库精确重现。要实现一比一视觉效果，需在 UE 编辑器运行脚本、补齐高度图/粒子数据，并用 Unity 原场景截图作为参考完成调试。
