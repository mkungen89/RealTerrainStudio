// Copyright RealTerrain Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Components/SplineComponent.h"
#include "RealTerrainOSMSplineImporter.generated.h"

class ALandscape;
class USplineComponent;
class AActor;

/**
 * Spline point data from OSM
 */
USTRUCT(BlueprintType)
struct FRealTerrainSplinePoint
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FVector Position = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FVector ArriveTangent = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FVector LeaveTangent = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FRotator Rotation = FRotator::ZeroRotator;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FVector Scale = FVector(1.0f, 1.0f, 1.0f);
};

/**
 * Road spline data
 */
USTRUCT(BlueprintType)
struct FRealTerrainRoadSpline
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString SplineID;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString Name;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	TArray<FRealTerrainSplinePoint> Points;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString RoadType; // motorway, primary, secondary, etc.

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	float Width = 400.0f; // cm

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	int32 Lanes = 2;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString Surface; // asphalt, gravel, dirt

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	bool bIsOneWay = false;
};

/**
 * Railway spline data
 */
USTRUCT(BlueprintType)
struct FRealTerrainRailwaySpline
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString SplineID;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	TArray<FRealTerrainSplinePoint> Points;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString RailwayType; // rail, subway, tram

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	int32 Tracks = 1;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	bool bElectrified = false;
};

/**
 * Power line spline data
 */
USTRUCT(BlueprintType)
struct FRealTerrainPowerLineSpline
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString SplineID;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	TArray<FRealTerrainSplinePoint> CablePoints;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	TArray<FVector> TowerPositions;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	int32 Cables = 3;

	UPROPERTY(BlueprintReadOnly, Category = "RealTerrain")
	FString Voltage;
};

/**
 * OSM Spline Importer for RealTerrain Studio
 * Handles importing OSM linear features as UE5 splines
 */
UCLASS()
class REALTERRAINSTUDIO_API URealTerrainOSMSplineImporter : public UObject
{
	GENERATED_BODY()

public:
	URealTerrainOSMSplineImporter();

	/**
	 * Import OSM splines from JSON file
	 * @param FilePath Path to OSM splines JSON file
	 * @param Landscape Target Landscape for positioning
	 * @return True if import succeeded
	 */
	UFUNCTION(BlueprintCallable, Category = "RealTerrain")
	bool ImportOSMSplines(const FString& FilePath, ALandscape* Landscape);

	/**
	 * Create road spline actor
	 * @param RoadData Road spline data
	 * @param Landscape Landscape for positioning
	 * @return Created spline actor
	 */
	AActor* CreateRoadSpline(const FRealTerrainRoadSpline& RoadData, ALandscape* Landscape);

	/**
	 * Create railway spline actor
	 * @param RailwayData Railway spline data
	 * @param Landscape Landscape for positioning
	 * @return Created spline actor
	 */
	AActor* CreateRailwaySpline(const FRealTerrainRailwaySpline& RailwayData, ALandscape* Landscape);

	/**
	 * Create power line spline actor
	 * @param PowerLineData Power line spline data
	 * @param Landscape Landscape for positioning
	 * @return Created spline actor
	 */
	AActor* CreatePowerLineSpline(const FRealTerrainPowerLineSpline& PowerLineData, ALandscape* Landscape);

private:
	/**
	 * Parse OSM splines JSON file
	 * @param FilePath Path to JSON file
	 * @param OutRoads Parsed road splines
	 * @param OutRailways Parsed railway splines
	 * @param OutPowerLines Parsed power line splines
	 * @return True if parsing succeeded
	 */
	bool ParseOSMSplinesJSON(const FString& FilePath,
		TArray<FRealTerrainRoadSpline>& OutRoads,
		TArray<FRealTerrainRailwaySpline>& OutRailways,
		TArray<FRealTerrainPowerLineSpline>& OutPowerLines);

	/**
	 * Create spline component with points
	 * @param Owner Owner actor
	 * @param Points Spline points
	 * @return Created spline component
	 */
	USplineComponent* CreateSplineComponent(AActor* Owner, const TArray<FRealTerrainSplinePoint>& Points);

	/**
	 * Calculate spline tangents for smooth curves
	 * @param Points Input points
	 */
	void CalculateSplineTangents(TArray<FRealTerrainSplinePoint>& Points);
};
