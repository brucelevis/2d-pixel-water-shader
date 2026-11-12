using UnrealBuildTool;
using System.Collections.Generic;

public class PixelWaterUE57Target : TargetRules
{
    public PixelWaterUE57Target(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_7;
        bUseUnityBuild = false;
        bUsePCHFiles = false;

        ExtraModuleNames.Add("PixelWaterUE57");
    }
}
