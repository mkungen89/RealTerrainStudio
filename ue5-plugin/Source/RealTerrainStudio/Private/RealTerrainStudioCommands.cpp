// Copyright RealTerrain Studio. All Rights Reserved.

#include "RealTerrainStudioCommands.h"

#define LOCTEXT_NAMESPACE "FRealTerrainStudioModule"

void FRealTerrainStudioCommands::RegisterCommands()
{
	UI_COMMAND(OpenPluginWindow, "RealTerrain Studio", "Import real-world terrain data", EUserInterfaceActionType::Button, FInputChord());
}

#undef LOCTEXT_NAMESPACE
