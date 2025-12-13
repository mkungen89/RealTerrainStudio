// Copyright RealTerrain Studio. All Rights Reserved.

using UnrealBuildTool;

public class RealTerrainStudio : ModuleRules
{
	public RealTerrainStudio(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
		);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				"Json",
				"JsonUtilities",
				"ImageWrapper",
				"Projects"
			}
		);

		// Editor-only dependencies
		if (Target.Type == TargetType.Editor)
		{
			PrivateDependencyModuleNames.AddRange(
				new string[]
				{
					"UnrealEd",
					"LevelEditor",
					"Landscape",
					"LandscapeEditor",
					"EditorScriptingUtilities",
					"AssetTools",
					"ContentBrowser",
					"ToolMenus",
					"DesktopPlatform",
					"Foliage"
				}
			);
		}

		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
		);
	}
}
