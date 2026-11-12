// UE 5.7 Material Custom node reference. Output Type: Float4.
// Add the pins listed in UE5_Migration.md. Texture pins must be Texture2D objects;
// sampler pins must be SamplerState inputs. This is a shader expression body, not a
// standalone Unreal shader file or a serialized Material asset.

float2 grid = max(PixelGrid, float2(1.0, 1.0));
float2 pixelUV = (floor(UV * grid) + 0.5) / grid;
float2 worldUV = WorldPosition.xy * WorldTextureScale + WorldTextureOffset;

float2 flowA = Time * float2(CausticSpeed, CausticSpeed * 0.73);
float2 flowB = -Time * float2(CausticSpeed * 0.61, CausticSpeed * 0.89);
float2 causticUV = pixelUV * CausticScale + worldUV * CausticMovementAmount + flowA;
float2 highlightUV = pixelUV * CausticScale * 1.37 + worldUV * CausticMovementAmount - flowB;

float causticA = Texture2DSample(CausticTexture, CausticTextureSampler, causticUV).r;
float causticB = Texture2DSample(CausticHighlightTexture, CausticHighlightSampler, highlightUV).r;
float caustic = saturate((causticA + causticB * CausticHighlightStrength - CausticThreshold) * CausticFaderScale);

// Fixed 3x3 box blur approximation for the foam mask.
float foam = 0.0;
[unroll]
for (int x = -1; x <= 1; ++x)
{
    [unroll]
    for (int y = -1; y <= 1; ++y)
    {
        float2 offset = float2(x, y) * FoamTexelSize * max(FoamBlur, 1.0);
        foam += Texture2DSample(FoamTexture, FoamTextureSampler, pixelUV * FoamScale + worldUV + offset).a;
    }
}
foam /= 9.0;

float specWave = sin((pixelUV.x + worldUV.x) * SpecularScale + Time * SpecularSpeed)
               * sin((pixelUV.y + worldUV.y) * SpecularScale2 - Time * SpecularSpeed);
float specular = step(SpecularThreshold, specWave) * SpecularColour.a;

float3 water = MainColour.rgb;
water += CausticColour.rgb * caustic * CausticColour.a;
water = lerp(water, FoamColour.rgb, saturate(foam * FoamColour.a));
water += SpecularColour.rgb * specular;
float alpha = saturate(MainColour.a + caustic * CausticColour.a + foam * FoamColour.a);
return float4(water, alpha);
