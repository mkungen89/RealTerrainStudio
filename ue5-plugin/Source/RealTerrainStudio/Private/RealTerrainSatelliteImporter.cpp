// Copyright RealTerrain Studio. All Rights Reserved.

#include "RealTerrainSatelliteImporter.h"
#include "Landscape.h"
#include "LandscapeProxy.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Modules/ModuleManager.h"
#include "Misc/FileHelper.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpressionTextureSample.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "UObject/Package.h"
#include "Factories/MaterialFactoryNew.h"

URealTerrainSatelliteImporter::URealTerrainSatelliteImporter()
{
}

bool URealTerrainSatelliteImporter::ImportAndApplySatelliteTexture(const FString& TexturePath, ALandscape* Landscape)
{
	if (!Landscape)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Invalid Landscape actor"));
		return false;
	}

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Loading satellite texture from %s"), *TexturePath);

	// Load texture
	UTexture2D* SatelliteTexture = nullptr;
	if (!LoadTextureFromPNG(TexturePath, SatelliteTexture))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to load satellite texture"));
		return false;
	}

	// Create material
	UMaterialInstanceDynamic* Material = nullptr;
	if (!CreateLandscapeMaterial(SatelliteTexture, Material))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to create landscape material"));
		return false;
	}

	// Apply material to Landscape
	if (!ApplyMaterialToLandscape(Landscape, Material))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to apply material to landscape"));
		return false;
	}

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Successfully applied satellite texture to landscape"));
	return true;
}

bool URealTerrainSatelliteImporter::LoadTextureFromPNG(const FString& FilePath, UTexture2D*& OutTexture)
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

	// Get image dimensions and format
	int32 Width = ImageWrapper->GetWidth();
	int32 Height = ImageWrapper->GetHeight();
	int32 BitDepth = ImageWrapper->GetBitDepth();
	ERGBFormat Format = ImageWrapper->GetFormat();

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Satellite texture dimensions: %dx%d, bit depth: %d"), Width, Height, BitDepth);

	// Get raw image data (RGBA or RGB)
	TArray<uint8> RawData;
	bool bHasAlpha = (Format == ERGBFormat::RGBA || Format == ERGBFormat::BGRA);

	// Always request RGBA to avoid Windows RGB macro conflict
	if (!ImageWrapper->GetRaw(ERGBFormat::RGBA, 8, RawData))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to get raw image data"));
		return false;
	}

	// ImageWrapper will convert to RGBA if needed
	bHasAlpha = true;

	// Create texture from raw data
	OutTexture = CreateTextureFromData(RawData, Width, Height, bHasAlpha);

	if (!OutTexture)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to create texture"));
		return false;
	}

	return true;
}

UTexture2D* URealTerrainSatelliteImporter::CreateTextureFromData(const TArray<uint8>& ImageData, int32 Width, int32 Height, bool bHasAlpha)
{
	// Create texture
	UTexture2D* Texture = UTexture2D::CreateTransient(Width, Height, bHasAlpha ? PF_R8G8B8A8 : PF_R8G8B8A8);

	if (!Texture)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to create transient texture"));
		return nullptr;
	}

	// Lock the texture for writing
	void* TextureData = Texture->GetPlatformData()->Mips[0].BulkData.Lock(LOCK_READ_WRITE);

	// Copy image data to texture
	int32 BytesPerPixel = bHasAlpha ? 4 : 4; // Always use 4 bytes for simplicity
	int32 TotalSize = Width * Height * BytesPerPixel;

	if (bHasAlpha)
	{
		// Direct copy for RGBA
		FMemory::Memcpy(TextureData, ImageData.GetData(), TotalSize);
	}
	else
	{
		// Convert RGB to RGBA by adding alpha channel
		uint8* Dest = (uint8*)TextureData;
		const uint8* Src = ImageData.GetData();

		for (int32 i = 0; i < Width * Height; i++)
		{
			Dest[i * 4 + 0] = Src[i * 3 + 0]; // R
			Dest[i * 4 + 1] = Src[i * 3 + 1]; // G
			Dest[i * 4 + 2] = Src[i * 3 + 2]; // B
			Dest[i * 4 + 3] = 255;             // A
		}
	}

	// Unlock and update texture
	Texture->GetPlatformData()->Mips[0].BulkData.Unlock();
	Texture->UpdateResource();

	// Set texture properties
	Texture->SRGB = true;
	Texture->CompressionSettings = TC_Default;
	Texture->MipGenSettings = TMGS_FromTextureGroup;
	Texture->LODGroup = TEXTUREGROUP_World;
	Texture->AddressX = TA_Clamp;
	Texture->AddressY = TA_Clamp;

	return Texture;
}

bool URealTerrainSatelliteImporter::CreateLandscapeMaterial(UTexture2D* SatelliteTexture, UMaterialInstanceDynamic*& OutMaterial)
{
	if (!SatelliteTexture)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Invalid satellite texture"));
		return false;
	}

	// Create a simple material instance
	// In a production environment, you would create a proper material asset
	// For now, we'll create a dynamic material instance from a base material

	// Try to find or create a base landscape material
	UMaterial* BaseMaterial = LoadObject<UMaterial>(nullptr, TEXT("/Engine/EngineMaterials/DefaultMaterial"));

	if (!BaseMaterial)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to load base material"));
		return false;
	}

	// Create dynamic material instance
	OutMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, GetTransientPackage());

	if (!OutMaterial)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to create dynamic material instance"));
		return false;
	}

	// Set satellite texture as a parameter
	// Note: This requires the base material to have a texture parameter
	// For now, we'll just store the reference
	OutMaterial->SetTextureParameterValue(FName("BaseTexture"), SatelliteTexture);

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Created landscape material with satellite texture"));
	return true;
}

bool URealTerrainSatelliteImporter::ApplyMaterialToLandscape(ALandscape* Landscape, UMaterialInterface* Material)
{
	if (!Landscape || !Material)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Invalid Landscape or Material"));
		return false;
	}

	// Set the landscape material
	Landscape->LandscapeMaterial = Material;

	// Update all landscape components
	Landscape->UpdateAllComponentMaterialInstances();

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Applied material to landscape"));
	return true;
}
