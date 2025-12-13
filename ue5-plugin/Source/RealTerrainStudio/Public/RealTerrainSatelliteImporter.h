// Copyright RealTerrain Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "RealTerrainSatelliteImporter.generated.h"

class ALandscape;
class UTexture2D;
class UMaterialInterface;
class UMaterialInstanceDynamic;

/**
 * Satellite Texture Importer for RealTerrain Studio
 * Handles loading satellite imagery and applying it to Landscape materials
 */
UCLASS()
class REALTERRAINSTUDIO_API URealTerrainSatelliteImporter : public UObject
{
	GENERATED_BODY()

public:
	URealTerrainSatelliteImporter();

	/**
	 * Import satellite texture and apply to Landscape
	 * @param TexturePath Path to satellite texture PNG file
	 * @param Landscape Target Landscape actor
	 * @return True if import succeeded
	 */
	UFUNCTION(BlueprintCallable, Category = "RealTerrain")
	bool ImportAndApplySatelliteTexture(const FString& TexturePath, ALandscape* Landscape);

	/**
	 * Load PNG texture from file
	 * @param FilePath Path to PNG file
	 * @param OutTexture Created texture
	 * @return True if loading succeeded
	 */
	bool LoadTextureFromPNG(const FString& FilePath, UTexture2D*& OutTexture);

	/**
	 * Create landscape material with satellite texture
	 * @param SatelliteTexture Satellite imagery texture
	 * @param OutMaterial Created material instance
	 * @return True if creation succeeded
	 */
	bool CreateLandscapeMaterial(UTexture2D* SatelliteTexture, UMaterialInstanceDynamic*& OutMaterial);

	/**
	 * Apply material to Landscape
	 * @param Landscape Target Landscape actor
	 * @param Material Material to apply
	 * @return True if application succeeded
	 */
	bool ApplyMaterialToLandscape(ALandscape* Landscape, UMaterialInterface* Material);

private:
	/**
	 * Create texture from raw image data
	 * @param ImageData Raw pixel data
	 * @param Width Image width
	 * @param Height Image height
	 * @param bHasAlpha Whether image has alpha channel
	 * @return Created texture
	 */
	UTexture2D* CreateTextureFromData(const TArray<uint8>& ImageData, int32 Width, int32 Height, bool bHasAlpha);
};
