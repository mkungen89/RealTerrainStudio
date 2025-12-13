// Copyright RealTerrain Studio. All Rights Reserved.

#include "RealTerrainStudio.h"
#include "RealTerrainStudioStyle.h"
#include "RealTerrainStudioCommands.h"
#include "RealTerrainHeightmapImporter.h"
#include "RealTerrainSatelliteImporter.h"
#include "RealTerrainOSMSplineImporter.h"
#include "LevelEditor.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"
#include "ToolMenus.h"
#include "Misc/MessageDialog.h"
#include "DesktopPlatformModule.h"
#include "IDesktopPlatform.h"
#include "Misc/Paths.h"
#include "Landscape.h"

static const FName RealTerrainStudioTabName("RealTerrainStudio");

#define LOCTEXT_NAMESPACE "FRealTerrainStudioModule"

void FRealTerrainStudioModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module

	FRealTerrainStudioStyle::Initialize();
	FRealTerrainStudioStyle::ReloadTextures();

	FRealTerrainStudioCommands::Register();

	PluginCommands = MakeShareable(new FUICommandList);

	PluginCommands->MapAction(
		FRealTerrainStudioCommands::Get().OpenPluginWindow,
		FExecuteAction::CreateRaw(this, &FRealTerrainStudioModule::PluginButtonClicked),
		FCanExecuteAction());

	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FRealTerrainStudioModule::RegisterMenus));
}

void FRealTerrainStudioModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.

	UToolMenus::UnRegisterStartupCallback(this);

	UToolMenus::UnregisterOwner(this);

	FRealTerrainStudioStyle::Shutdown();

	FRealTerrainStudioCommands::Unregister();
}

void FRealTerrainStudioModule::PluginButtonClicked()
{
	// Open file picker dialog
	IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();
	if (!DesktopPlatform)
	{
		FMessageDialog::Open(EAppMsgType::Ok, LOCTEXT("ErrorNoPlatform", "Failed to get desktop platform module"));
		return;
	}

	TArray<FString> OpenFilenames;
	const FString FileTypes = TEXT("RealTerrain Heightmap (*.png)|*.png");
	const FString DefaultPath = FPaths::ProjectContentDir();

	bool bOpened = DesktopPlatform->OpenFileDialog(
		nullptr,
		TEXT("Select RealTerrain Heightmap"),
		DefaultPath,
		TEXT(""),
		FileTypes,
		EFileDialogFlags::None,
		OpenFilenames
	);

	if (bOpened && OpenFilenames.Num() > 0)
	{
		FString HeightmapPath = OpenFilenames[0];

		// Construct metadata path (same directory, same name, .json extension)
		FString MetadataPath = FPaths::GetPath(HeightmapPath) / TEXT("metadata.json");

		// Check if metadata file exists
		if (!FPaths::FileExists(MetadataPath))
		{
			FText ErrorMsg = FText::Format(
				LOCTEXT("ErrorNoMetadata", "Metadata file not found:\n{0}\n\nExpected metadata.json in the same directory as the heightmap."),
				FText::FromString(MetadataPath)
			);
			FMessageDialog::Open(EAppMsgType::Ok, ErrorMsg);
			return;
		}

		// Import heightmap
		URealTerrainHeightmapImporter* Importer = NewObject<URealTerrainHeightmapImporter>();
		ALandscape* Landscape = nullptr;

		if (Importer->ImportHeightmap(HeightmapPath, MetadataPath, Landscape))
		{
			// Check for satellite texture
			FString SatellitePath = FPaths::GetPath(HeightmapPath) / TEXT("satellite_texture.png");

			if (FPaths::FileExists(SatellitePath))
			{
				UE_LOG(LogTemp, Log, TEXT("RealTerrain: Found satellite texture, applying..."));

				URealTerrainSatelliteImporter* SatelliteImporter = NewObject<URealTerrainSatelliteImporter>();
				if (SatelliteImporter->ImportAndApplySatelliteTexture(SatellitePath, Landscape))
				{
					UE_LOG(LogTemp, Log, TEXT("RealTerrain: Satellite texture applied successfully"));
				}
				else
				{
					UE_LOG(LogTemp, Warning, TEXT("RealTerrain: Failed to apply satellite texture"));
				}
			}

			// Check for OSM splines
			FString OSMSplinesPath = FPaths::GetPath(HeightmapPath) / TEXT("osm_splines.json");

			if (FPaths::FileExists(OSMSplinesPath))
			{
				UE_LOG(LogTemp, Log, TEXT("RealTerrain: Found OSM splines data, importing..."));

				URealTerrainOSMSplineImporter* SplineImporter = NewObject<URealTerrainOSMSplineImporter>();
				if (SplineImporter->ImportOSMSplines(OSMSplinesPath, Landscape))
				{
					UE_LOG(LogTemp, Log, TEXT("RealTerrain: OSM splines imported successfully"));
				}
				else
				{
					UE_LOG(LogTemp, Warning, TEXT("RealTerrain: Failed to import OSM splines"));
				}
			}

			FText SuccessMsg = FText::Format(
				LOCTEXT("ImportSuccess", "Successfully imported heightmap!\n\nLandscape created: {0}"),
				FText::FromString(Landscape ? Landscape->GetActorLabel() : TEXT("Unknown"))
			);
			FMessageDialog::Open(EAppMsgType::Ok, SuccessMsg);
		}
		else
		{
			FMessageDialog::Open(EAppMsgType::Ok,
				LOCTEXT("ImportFailed", "Failed to import heightmap. Check the Output Log for details."));
		}
	}
}

void FRealTerrainStudioModule::RegisterMenus()
{
	// Owner will be used for cleanup in call to UToolMenus::UnregisterOwner
	FToolMenuOwnerScoped OwnerScoped(this);

	{
		UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
		{
			FToolMenuSection& Section = Menu->FindOrAddSection("WindowLayout");
			Section.AddMenuEntryWithCommandList(FRealTerrainStudioCommands::Get().OpenPluginWindow, PluginCommands);
		}
	}

	{
		UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar");
		{
			FToolMenuSection& Section = ToolbarMenu->FindOrAddSection("Settings");
			{
				FToolMenuEntry& Entry = Section.AddEntry(FToolMenuEntry::InitToolBarButton(FRealTerrainStudioCommands::Get().OpenPluginWindow));
				Entry.SetCommandList(PluginCommands);
			}
		}
	}
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FRealTerrainStudioModule, RealTerrainStudio)
