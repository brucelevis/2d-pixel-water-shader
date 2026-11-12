using UnrealBuildTool;
using System.Collections.Generic;

public class PixelWaterUE57EditorTarget : TargetRules
{
    public PixelWaterUE57EditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_7;
        bUseUnityBuild = false;
        bUsePCHFiles = false;

        ExtraModuleNames.Add("PixelWaterUE57");
    }
}
