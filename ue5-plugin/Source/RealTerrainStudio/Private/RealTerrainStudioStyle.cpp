// Copyright RealTerrain Studio. All Rights Reserved.

#include "RealTerrainStudioStyle.h"
#include "Styling/SlateStyleRegistry.h"
#include "Framework/Application/SlateApplication.h"
#include "Slate/SlateGameResources.h"
#include "Interfaces/IPluginManager.h"
#include "Styling/SlateStyleMacros.h"

#define RootToContentDir Style->RootToContentDir

TSharedPtr<FSlateStyleSet> FRealTerrainStudioStyle::StyleInstance = nullptr;

void FRealTerrainStudioStyle::Initialize()
{
	if (!StyleInstance.IsValid())
	{
		StyleInstance = Create();
		FSlateStyleRegistry::RegisterSlateStyle(*StyleInstance);
	}
}

void FRealTerrainStudioStyle::Shutdown()
{
	FSlateStyleRegistry::UnRegisterSlateStyle(*StyleInstance);
	ensure(StyleInstance.IsUnique());
	StyleInstance.Reset();
}

FName FRealTerrainStudioStyle::GetStyleSetName()
{
	static FName StyleSetName(TEXT("RealTerrainStudioStyle"));
	return StyleSetName;
}

const FVector2D Icon16x16(16.0f, 16.0f);
const FVector2D Icon20x20(20.0f, 20.0f);
const FVector2D Icon40x40(40.0f, 40.0f);

TSharedRef< FSlateStyleSet > FRealTerrainStudioStyle::Create()
{
	TSharedRef< FSlateStyleSet > Style = MakeShareable(new FSlateStyleSet("RealTerrainStudioStyle"));
	Style->SetContentRoot(IPluginManager::Get().FindPlugin("RealTerrainStudio")->GetBaseDir() / TEXT("Resources"));

	Style->Set("RealTerrainStudio.OpenPluginWindow", new IMAGE_BRUSH_SVG(TEXT("PlaceholderButtonIcon"), Icon40x40));

	return Style;
}

void FRealTerrainStudioStyle::ReloadTextures()
{
	if (FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().GetRenderer()->ReloadTextureResources();
	}
}

const ISlateStyle& FRealTerrainStudioStyle::Get()
{
	return *StyleInstance;
}
