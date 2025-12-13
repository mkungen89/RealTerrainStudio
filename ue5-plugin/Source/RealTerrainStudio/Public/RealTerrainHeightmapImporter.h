// Copyright RealTerrain Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "RealTerrainHeightmapImporter.generated.h"

class ALandscape;

/**
 * Metadata structure for terrain import
 */
USTRUCT(BlueprintType)
struct FRealTerrainMetadata
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	int32 Width = 0;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	int32 Height = 0;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	float MinElevation = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	float MaxElevation = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	float PixelSizeX = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	float PixelSizeY = 0.0f;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString CRS;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	TArray<float> BoundsMinXY;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	TArray<float> BoundsMaxXY;
};

/**
 * Heightmap Importer for RealTerrain Studio
 * Handles importing 16-bit PNG heightmaps and creating Landscape actors
 */
UCLASS()
class REALTERRAINSTUDIO_API URealTerrainHeightmapImporter : public UObject
{
	GENERATED_BODY()

public:
	URealTerrainHeightmapImporter();

	/**
	 * Import heightmap and create Landscape
	 * @param HeightmapPath Path to 16-bit PNG heightmap file
	 * @param MetadataPath Path to metadata JSON file
	 * @param OutLandscape Created Landscape actor
	 * @return True if import succeeded
	 */
	UFUNCTION(BlueprintCallable, Category = "RealTerrain")
	bool ImportHeightmap(const FString& HeightmapPath, const FString& MetadataPath, ALandscape*& OutLandscape);

	/**
	 * Read 16-bit PNG heightmap data
	 * @param FilePath Path to PNG file
	 * @param OutData Output heightmap data (0-65535 range)
	 * @param OutWidth Width of heightmap
	 * @param OutHeight Height of heightmap
	 * @return True if read succeeded
	 */
	bool Read16BitPNG(const FString& FilePath, TArray<uint16>& OutData, int32& OutWidth, int32& OutHeight);

	/**
	 * Parse metadata JSON file
	 * @param FilePath Path to JSON file
	 * @param OutMetadata Parsed metadata structure
	 * @return True if parsing succeeded
	 */
	bool ParseMetadata(const FString& FilePath, FRealTerrainMetadata& OutMetadata);

	/**
	 * Create Landscape actor from heightmap data
	 * @param HeightmapData 16-bit heightmap data
	 * @param Metadata Terrain metadata
	 * @param OutLandscape Created Landscape actor
	 * @return True if creation succeeded
	 */
	bool CreateLandscape(const TArray<uint16>& HeightmapData, const FRealTerrainMetadata& Metadata, ALandscape*& OutLandscape);

private:
	/**
	 * Calculate optimal Landscape component configuration
	 * @param Width Heightmap width
	 * @param Height Heightmap height
	 * @param OutComponentCountX Number of components in X
	 * @param OutComponentCountY Number of components in Y
	 * @param OutQuadsPerComponent Quads per component
	 * @param OutSectionsPerComponent Sections per component
	 */
	void CalculateLandscapeConfiguration(int32 Width, int32 Height,
		int32& OutComponentCountX, int32& OutComponentCountY,
		int32& OutQuadsPerComponent, int32& OutSectionsPerComponent);

	/**
	 * Convert 16-bit heightmap data to UE5 format
	 * @param InputData 16-bit heightmap data
	 * @param Metadata Terrain metadata
	 * @return Converted heightmap data for UE5
	 */
	TArray<uint16> ConvertHeightmapToUE5Format(const TArray<uint16>& InputData, const FRealTerrainMetadata& Metadata);
};
