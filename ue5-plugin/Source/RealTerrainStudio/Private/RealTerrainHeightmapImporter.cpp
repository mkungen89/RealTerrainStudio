// Copyright RealTerrain Studio. All Rights Reserved.

#include "RealTerrainHeightmapImporter.h"
#include "Landscape.h"
#include "LandscapeInfo.h"
#include "LandscapeComponent.h"
#include "LandscapeEdit.h"
#include "LandscapeEditorModule.h"
#include "LandscapeDataAccess.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Modules/ModuleManager.h"
#include "Misc/FileHelper.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Engine/World.h"
#include "Editor.h"

URealTerrainHeightmapImporter::URealTerrainHeightmapImporter()
{
}

bool URealTerrainHeightmapImporter::ImportHeightmap(const FString& HeightmapPath, const FString& MetadataPath, ALandscape*& OutLandscape)
{
	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Starting heightmap import from %s"), *HeightmapPath);

	// Read metadata
	FRealTerrainMetadata Metadata;
	if (!ParseMetadata(MetadataPath, Metadata))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to parse metadata from %s"), *MetadataPath);
		return false;
	}

	// Read heightmap
	TArray<uint16> HeightmapData;
	int32 Width, Height;
	if (!Read16BitPNG(HeightmapPath, HeightmapData, Width, Height))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to read heightmap from %s"), *HeightmapPath);
		return false;
	}

	// Validate dimensions
	if (Width != Metadata.Width || Height != Metadata.Height)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Heightmap dimensions (%dx%d) do not match metadata (%dx%d)"),
			Width, Height, Metadata.Width, Metadata.Height);
		return false;
	}

	// Create Landscape
	if (!CreateLandscape(HeightmapData, Metadata, OutLandscape))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to create Landscape"));
		return false;
	}

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Successfully imported heightmap"));
	return true;
}

bool URealTerrainHeightmapImporter::Read16BitPNG(const FString& FilePath, TArray<uint16>& OutData, int32& OutWidth, int32& OutHeight)
{
	// Load file into byte array
	TArray<uint8> FileData;
	if (!FFileHelper::LoadFileToArray(FileData, *FilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to load PNG file: %s"), *FilePath);
		return false;
	}

	// Get image wrapper module
	IImageWrapperModule& ImageWrapperModule = FModuleManager::LoadModuleChecked<IImageWrapperModule>(FName("ImageWrapper"));
	TSharedPtr<IImageWrapper> ImageWrapper = ImageWrapperModule.CreateImageWrapper(EImageFormat::PNG);

	if (!ImageWrapper.IsValid() || !ImageWrapper->SetCompressed(FileData.GetData(), FileData.Num()))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to decompress PNG file: %s"), *FilePath);
		return false;
	}

	// Get image dimensions
	OutWidth = ImageWrapper->GetWidth();
	OutHeight = ImageWrapper->GetHeight();
	int32 BitDepth = ImageWrapper->GetBitDepth();

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: PNG dimensions: %dx%d, bit depth: %d"), OutWidth, OutHeight, BitDepth);

	// Get raw image data
	TArray<uint8> RawData;
	if (!ImageWrapper->GetRaw(ERGBFormat::Gray, BitDepth, RawData))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to get raw image data"));
		return false;
	}

	// Convert to uint16 array
	if (BitDepth == 16)
	{
		// 16-bit grayscale: 2 bytes per pixel
		int32 PixelCount = OutWidth * OutHeight;
		OutData.SetNum(PixelCount);

		for (int32 i = 0; i < PixelCount; i++)
		{
			// PNG stores as big-endian, convert to uint16
			uint16 Value = (uint16(RawData[i * 2]) << 8) | uint16(RawData[i * 2 + 1]);
			OutData[i] = Value;
		}
	}
	else if (BitDepth == 8)
	{
		// 8-bit grayscale: scale to 16-bit
		int32 PixelCount = OutWidth * OutHeight;
		OutData.SetNum(PixelCount);

		for (int32 i = 0; i < PixelCount; i++)
		{
			OutData[i] = uint16(RawData[i]) * 257; // Scale 0-255 to 0-65535
		}
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Unsupported bit depth: %d"), BitDepth);
		return false;
	}

	return true;
}

bool URealTerrainHeightmapImporter::ParseMetadata(const FString& FilePath, FRealTerrainMetadata& OutMetadata)
{
	// Load JSON file
	FString JsonString;
	if (!FFileHelper::LoadFileToString(JsonString, *FilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to load metadata file: %s"), *FilePath);
		return false;
	}

	// Parse JSON
	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);

	if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to parse JSON metadata"));
		return false;
	}

	// Extract heightmap data
	const TSharedPtr<FJsonObject>* HeightmapObject;
	if (!JsonObject->TryGetObjectField(TEXT("heightmap"), HeightmapObject))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Missing 'heightmap' field in metadata"));
		return false;
	}

	OutMetadata.Width = (*HeightmapObject)->GetIntegerField(TEXT("width"));
	OutMetadata.Height = (*HeightmapObject)->GetIntegerField(TEXT("height"));
	OutMetadata.MinElevation = (*HeightmapObject)->GetNumberField(TEXT("min_elevation"));
	OutMetadata.MaxElevation = (*HeightmapObject)->GetNumberField(TEXT("max_elevation"));
	OutMetadata.PixelSizeX = (*HeightmapObject)->GetNumberField(TEXT("pixel_size_x"));
	OutMetadata.PixelSizeY = (*HeightmapObject)->GetNumberField(TEXT("pixel_size_y"));
	OutMetadata.CRS = (*HeightmapObject)->GetStringField(TEXT("crs"));

	// Extract bounds
	const TArray<TSharedPtr<FJsonValue>>* BoundsArray;
	if ((*HeightmapObject)->TryGetArrayField(TEXT("bounds"), BoundsArray))
	{
		if (BoundsArray->Num() == 4)
		{
			OutMetadata.BoundsMinXY.Add((*BoundsArray)[0]->AsNumber());
			OutMetadata.BoundsMinXY.Add((*BoundsArray)[1]->AsNumber());
			OutMetadata.BoundsMaxXY.Add((*BoundsArray)[2]->AsNumber());
			OutMetadata.BoundsMaxXY.Add((*BoundsArray)[3]->AsNumber());
		}
	}

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Metadata parsed - Size: %dx%d, Elevation: %.2f to %.2f"),
		OutMetadata.Width, OutMetadata.Height, OutMetadata.MinElevation, OutMetadata.MaxElevation);

	return true;
}

bool URealTerrainHeightmapImporter::CreateLandscape(const TArray<uint16>& HeightmapData, const FRealTerrainMetadata& Metadata, ALandscape*& OutLandscape)
{
	UWorld* World = GEditor->GetEditorWorldContext().World();
	if (!World)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: No valid world found"));
		return false;
	}

	// Calculate Landscape configuration
	int32 ComponentCountX, ComponentCountY, QuadsPerComponent, SectionsPerComponent;
	CalculateLandscapeConfiguration(Metadata.Width, Metadata.Height,
		ComponentCountX, ComponentCountY, QuadsPerComponent, SectionsPerComponent);

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Landscape config - Components: %dx%d, Quads/Component: %d, Sections/Component: %d"),
		ComponentCountX, ComponentCountY, QuadsPerComponent, SectionsPerComponent);

	// Calculate scale
	// UE5 uses cm as units, pixel size is in meters
	float ScaleX = Metadata.PixelSizeX * 100.0f; // Convert m to cm
	float ScaleY = Metadata.PixelSizeY * 100.0f;
	float ElevationRange = Metadata.MaxElevation - Metadata.MinElevation;
	float ScaleZ = ElevationRange / 512.0f; // Scale Z to use full 16-bit range efficiently

	FVector Scale(ScaleX, ScaleY, ScaleZ);

	// Convert heightmap data to UE5 format
	TArray<uint16> ConvertedData = ConvertHeightmapToUE5Format(HeightmapData, Metadata);

	// Create Landscape actor first
	FActorSpawnParameters SpawnParams;
	SpawnParams.bNoFail = true;
	OutLandscape = World->SpawnActor<ALandscape>(FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

	if (!OutLandscape)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to spawn Landscape actor"));
		return false;
	}

	OutLandscape->SetActorLabel(TEXT("RealTerrain_Landscape"));
	OutLandscape->SetActorScale3D(Scale);

	// Configure landscape before importing data
	OutLandscape->ComponentSizeQuads = QuadsPerComponent;
	OutLandscape->SubsectionSizeQuads = QuadsPerComponent / SectionsPerComponent;
	OutLandscape->NumSubsections = SectionsPerComponent;

	// Create landscape components manually
	int32 MinX = 0;
	int32 MinY = 0;
	int32 MaxX = ComponentCountX - 1;
	int32 MaxY = ComponentCountY - 1;

	// Create the landscape info
	ULandscapeInfo* LandscapeInfo = OutLandscape->CreateLandscapeInfo();
	LandscapeInfo->Modify();

	// Create components
	for (int32 Y = MinY; Y <= MaxY; Y++)
	{
		for (int32 X = MinX; X <= MaxX; X++)
		{
			ULandscapeComponent* Component = NewObject<ULandscapeComponent>(
				OutLandscape,
				NAME_None,
				RF_Transactional
			);

			Component->Init(
				X * QuadsPerComponent,
				Y * QuadsPerComponent,
				OutLandscape->ComponentSizeQuads,
				OutLandscape->NumSubsections,
				OutLandscape->SubsectionSizeQuads
			);

			Component->SetupAttachment(OutLandscape->GetRootComponent());
			Component->RegisterComponent();

			OutLandscape->LandscapeComponents.Add(Component);
			LandscapeInfo->XYtoComponentMap.Add(FIntPoint(X, Y), Component);
		}
	}

	// Now set the heightmap data using the landscape edit data interface
	FLandscapeEditDataInterface LandscapeEdit(LandscapeInfo);

	// Set heightmap data for the entire landscape using batch method
	// SetHeightData takes the data, min/max coordinates
	LandscapeEdit.SetHeightData(0, 0, Metadata.Width - 1, Metadata.Height - 1, ConvertedData.GetData(), 0, true);

	// Recreate render state
	OutLandscape->RecreateComponentsState();

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Landscape created successfully"));
	return true;
}

void URealTerrainHeightmapImporter::CalculateLandscapeConfiguration(int32 Width, int32 Height,
	int32& OutComponentCountX, int32& OutComponentCountY, int32& OutQuadsPerComponent, int32& OutSectionsPerComponent)
{
	// Valid quads per component: 7, 15, 31, 63, 127, 255
	// Valid sections per component: 1, 2
	const TArray<int32> ValidQuads = {7, 15, 31, 63, 127, 255};

	// Find best configuration
	OutSectionsPerComponent = 1;
	OutQuadsPerComponent = 63; // Default

	// Find the largest valid quad size that divides evenly
	for (int32 i = ValidQuads.Num() - 1; i >= 0; i--)
	{
		int32 QuadSize = ValidQuads[i];
		int32 VertexSize = QuadSize + 1;

		if ((Width - 1) % QuadSize == 0 && (Height - 1) % QuadSize == 0)
		{
			OutQuadsPerComponent = QuadSize;
			break;
		}
	}

	// Calculate component counts
	int32 VertexSize = OutQuadsPerComponent + 1;
	OutComponentCountX = (Width - 1) / OutQuadsPerComponent;
	OutComponentCountY = (Height - 1) / OutQuadsPerComponent;

	// If dimensions don't fit perfectly, adjust
	if (OutComponentCountX == 0) OutComponentCountX = 1;
	if (OutComponentCountY == 0) OutComponentCountY = 1;
}

TArray<uint16> URealTerrainHeightmapImporter::ConvertHeightmapToUE5Format(const TArray<uint16>& InputData, const FRealTerrainMetadata& Metadata)
{
	// UE5 expects heightmap data in a specific format
	// The data should already be in 0-65535 range from the PNG
	// We may need to flip Y axis depending on coordinate system

	TArray<uint16> OutputData = InputData;

	// Flip Y axis (PNG is top-down, UE5 is bottom-up)
	TArray<uint16> FlippedData;
	FlippedData.SetNum(OutputData.Num());

	for (int32 Y = 0; Y < Metadata.Height; Y++)
	{
		for (int32 X = 0; X < Metadata.Width; X++)
		{
			int32 SrcIndex = Y * Metadata.Width + X;
			int32 DstIndex = (Metadata.Height - 1 - Y) * Metadata.Width + X;
			FlippedData[DstIndex] = OutputData[SrcIndex];
		}
	}

	return FlippedData;
}
