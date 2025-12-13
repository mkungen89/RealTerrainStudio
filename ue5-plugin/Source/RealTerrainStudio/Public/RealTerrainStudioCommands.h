// Copyright RealTerrain Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Framework/Commands/Commands.h"
#include "RealTerrainStudioStyle.h"

class FRealTerrainStudioCommands : public TCommands<FRealTerrainStudioCommands>
{
public:

	FRealTerrainStudioCommands()
		: TCommands<FRealTerrainStudioCommands>(TEXT("RealTerrainStudio"), NSLOCTEXT("Contexts", "RealTerrainStudio", "RealTerrain Studio Plugin"), NAME_None, FRealTerrainStudioStyle::GetStyleSetName())
	{
	}

	// TCommands<> interface
	virtual void RegisterCommands() override;

public:
	TSharedPtr< FUICommandInfo > OpenPluginWindow;
};
