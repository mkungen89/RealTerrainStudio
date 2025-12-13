// Copyright RealTerrain Studio. All Rights Reserved.

#include "RealTerrainOSMSplineImporter.h"
#include "Landscape.h"
#include "Components/SplineComponent.h"
#include "GameFramework/Actor.h"
#include "Engine/World.h"
#include "Misc/FileHelper.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Editor.h"

URealTerrainOSMSplineImporter::URealTerrainOSMSplineImporter()
{
}

bool URealTerrainOSMSplineImporter::ImportOSMSplines(const FString& FilePath, ALandscape* Landscape)
{
	if (!Landscape)
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Invalid Landscape for OSM spline import"));
		return false;
	}

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Importing OSM splines from %s"), *FilePath);

	// Parse JSON file
	TArray<FRealTerrainRoadSpline> Roads;
	TArray<FRealTerrainRailwaySpline> Railways;
	TArray<FRealTerrainPowerLineSpline> PowerLines;

	if (!ParseOSMSplinesJSON(FilePath, Roads, Railways, PowerLines))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to parse OSM splines JSON"));
		return false;
	}

	// Create road splines
	for (const FRealTerrainRoadSpline& Road : Roads)
	{
		AActor* RoadActor = CreateRoadSpline(Road, Landscape);
		if (RoadActor)
		{
			UE_LOG(LogTemp, Log, TEXT("RealTerrain: Created road spline: %s"), *Road.Name);
		}
	}

	// Create railway splines
	for (const FRealTerrainRailwaySpline& Railway : Railways)
	{
		AActor* RailwayActor = CreateRailwaySpline(Railway, Landscape);
		if (RailwayActor)
		{
			UE_LOG(LogTemp, Log, TEXT("RealTerrain: Created railway spline"));
		}
	}

	// Create power line splines
	for (const FRealTerrainPowerLineSpline& PowerLine : PowerLines)
	{
		AActor* PowerLineActor = CreatePowerLineSpline(PowerLine, Landscape);
		if (PowerLineActor)
		{
			UE_LOG(LogTemp, Log, TEXT("RealTerrain: Created power line spline"));
		}
	}

	UE_LOG(LogTemp, Log, TEXT("RealTerrain: Imported %d roads, %d railways, %d power lines"),
		Roads.Num(), Railways.Num(), PowerLines.Num());

	return true;
}

AActor* URealTerrainOSMSplineImporter::CreateRoadSpline(const FRealTerrainRoadSpline& RoadData, ALandscape* Landscape)
{
	UWorld* World = Landscape->GetWorld();
	if (!World)
	{
		return nullptr;
	}

	// Create actor for the road spline
	FActorSpawnParameters SpawnParams;
	SpawnParams.Name = FName(*FString::Printf(TEXT("Road_%s"), *RoadData.SplineID));
	AActor* RoadActor = World->SpawnActor<AActor>(AActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

	if (!RoadActor)
	{
		return nullptr;
	}

	RoadActor->SetActorLabel(FString::Printf(TEXT("Road_%s"), *RoadData.Name));

	// Create spline component
	USplineComponent* SplineComp = CreateSplineComponent(RoadActor, RoadData.Points);
	if (SplineComp)
	{
		// Set spline properties for roads
		SplineComp->SetClosedLoop(false);
		SplineComp->Duration = RoadData.Points.Num() * 1.0f;
	}

	return RoadActor;
}

AActor* URealTerrainOSMSplineImporter::CreateRailwaySpline(const FRealTerrainRailwaySpline& RailwayData, ALandscape* Landscape)
{
	UWorld* World = Landscape->GetWorld();
	if (!World)
	{
		return nullptr;
	}

	// Create actor for the railway spline
	FActorSpawnParameters SpawnParams;
	SpawnParams.Name = FName(*FString::Printf(TEXT("Railway_%s"), *RailwayData.SplineID));
	AActor* RailwayActor = World->SpawnActor<AActor>(AActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

	if (!RailwayActor)
	{
		return nullptr;
	}

	RailwayActor->SetActorLabel(FString::Printf(TEXT("Railway_%s"), *RailwayData.SplineID));

	// Create spline component
	USplineComponent* SplineComp = CreateSplineComponent(RailwayActor, RailwayData.Points);
	if (SplineComp)
	{
		// Railways need very smooth curves
		SplineComp->SetClosedLoop(false);
	}

	return RailwayActor;
}

AActor* URealTerrainOSMSplineImporter::CreatePowerLineSpline(const FRealTerrainPowerLineSpline& PowerLineData, ALandscape* Landscape)
{
	UWorld* World = Landscape->GetWorld();
	if (!World)
	{
		return nullptr;
	}

	// Create actor for the power line spline
	FActorSpawnParameters SpawnParams;
	SpawnParams.Name = FName(*FString::Printf(TEXT("PowerLine_%s"), *PowerLineData.SplineID));
	AActor* PowerLineActor = World->SpawnActor<AActor>(AActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

	if (!PowerLineActor)
	{
		return nullptr;
	}

	PowerLineActor->SetActorLabel(FString::Printf(TEXT("PowerLine_%s"), *PowerLineData.SplineID));

	// Create spline component for cables (with catenary sag)
	USplineComponent* SplineComp = CreateSplineComponent(PowerLineActor, PowerLineData.CablePoints);
	if (SplineComp)
	{
		SplineComp->SetClosedLoop(false);
	}

	// TODO: Create tower positions as separate components

	return PowerLineActor;
}

bool URealTerrainOSMSplineImporter::ParseOSMSplinesJSON(const FString& FilePath,
	TArray<FRealTerrainRoadSpline>& OutRoads,
	TArray<FRealTerrainRailwaySpline>& OutRailways,
	TArray<FRealTerrainPowerLineSpline>& OutPowerLines)
{
	// Load JSON file
	FString JsonString;
	if (!FFileHelper::LoadFileToString(JsonString, *FilePath))
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to load OSM splines file: %s"), *FilePath);
		return false;
	}

	// Parse JSON
	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);

	if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("RealTerrain: Failed to parse OSM splines JSON"));
		return false;
	}

	// Parse roads
	const TArray<TSharedPtr<FJsonValue>>* RoadsArray;
	if (JsonObject->TryGetArrayField(TEXT("roads"), RoadsArray))
	{
		for (const TSharedPtr<FJsonValue>& RoadValue : *RoadsArray)
		{
			const TSharedPtr<FJsonObject>& RoadObj = RoadValue->AsObject();
			if (!RoadObj.IsValid())
			{
				continue;
			}

			FRealTerrainRoadSpline Road;
			Road.SplineID = RoadObj->GetStringField(TEXT("spline_id"));
			Road.Name = RoadObj->GetStringField(TEXT("name"));
			Road.RoadType = RoadObj->GetStringField(TEXT("road_type"));
			Road.Width = RoadObj->GetNumberField(TEXT("width"));
			Road.Lanes = RoadObj->GetIntegerField(TEXT("lanes"));
			Road.Surface = RoadObj->GetStringField(TEXT("surface"));
			Road.bIsOneWay = RoadObj->GetBoolField(TEXT("one_way"));

			// Parse spline points
			const TArray<TSharedPtr<FJsonValue>>* PointsArray;
			if (RoadObj->TryGetArrayField(TEXT("points"), PointsArray))
			{
				for (const TSharedPtr<FJsonValue>& PointValue : *PointsArray)
				{
					const TSharedPtr<FJsonObject>& PointObj = PointValue->AsObject();
					if (!PointObj.IsValid())
					{
						continue;
					}

					FRealTerrainSplinePoint Point;

					// Parse position
					const TArray<TSharedPtr<FJsonValue>>* PosArray;
					if (PointObj->TryGetArrayField(TEXT("position"), PosArray) && PosArray->Num() >= 3)
					{
						Point.Position.X = (*PosArray)[0]->AsNumber();
						Point.Position.Y = (*PosArray)[1]->AsNumber();
						Point.Position.Z = (*PosArray)[2]->AsNumber();
					}

					Road.Points.Add(Point);
				}
			}

			// Calculate tangents for smooth curves
			CalculateSplineTangents(Road.Points);

			OutRoads.Add(Road);
		}
	}

	// Parse railways
	const TArray<TSharedPtr<FJsonValue>>* RailwaysArray;
	if (JsonObject->TryGetArrayField(TEXT("railways"), RailwaysArray))
	{
		for (const TSharedPtr<FJsonValue>& RailwayValue : *RailwaysArray)
		{
			const TSharedPtr<FJsonObject>& RailwayObj = RailwayValue->AsObject();
			if (!RailwayObj.IsValid())
			{
				continue;
			}

			FRealTerrainRailwaySpline Railway;
			Railway.SplineID = RailwayObj->GetStringField(TEXT("spline_id"));
			Railway.Tracks = RailwayObj->GetIntegerField(TEXT("tracks"));
			Railway.bIsElectrified = RailwayObj->GetBoolField(TEXT("electrified"));
			Railway.Gauge = RailwayObj->GetNumberField(TEXT("gauge"));

			// Parse spline points
			const TArray<TSharedPtr<FJsonValue>>* PointsArray;
			if (RailwayObj->TryGetArrayField(TEXT("points"), PointsArray))
			{
				for (const TSharedPtr<FJsonValue>& PointValue : *PointsArray)
				{
					const TSharedPtr<FJsonObject>& PointObj = PointValue->AsObject();
					if (!PointObj.IsValid())
					{
						continue;
					}

					FRealTerrainSplinePoint Point;

					// Parse position
					const TArray<TSharedPtr<FJsonValue>>* PosArray;
					if (PointObj->TryGetArrayField(TEXT("position"), PosArray) && PosArray->Num() >= 3)
					{
						Point.Position.X = (*PosArray)[0]->AsNumber();
						Point.Position.Y = (*PosArray)[1]->AsNumber();
						Point.Position.Z = (*PosArray)[2]->AsNumber();
					}

					Railway.Points.Add(Point);
				}
			}

			// Calculate tangents for smooth curves
			CalculateSplineTangents(Railway.Points);

			OutRailways.Add(Railway);
		}
	}

	// Parse power lines
	const TArray<TSharedPtr<FJsonValue>>* PowerLinesArray;
	if (JsonObject->TryGetArrayField(TEXT("power_lines"), PowerLinesArray))
	{
		for (const TSharedPtr<FJsonValue>& PowerLineValue : *PowerLinesArray)
		{
			const TSharedPtr<FJsonObject>& PowerLineObj = PowerLineValue->AsObject();
			if (!PowerLineObj.IsValid())
			{
				continue;
			}

			FRealTerrainPowerLineSpline PowerLine;
			PowerLine.SplineID = PowerLineObj->GetStringField(TEXT("spline_id"));
			PowerLine.Cables = PowerLineObj->GetIntegerField(TEXT("cables"));
			PowerLine.Voltage = PowerLineObj->GetNumberField(TEXT("voltage"));

			// Parse cable points (with catenary sag)
			const TArray<TSharedPtr<FJsonValue>>* CablePointsArray;
			if (PowerLineObj->TryGetArrayField(TEXT("cable_points"), CablePointsArray))
			{
				for (const TSharedPtr<FJsonValue>& PointValue : *CablePointsArray)
				{
					const TSharedPtr<FJsonObject>& PointObj = PointValue->AsObject();
					if (!PointObj.IsValid())
					{
						continue;
					}

					FRealTerrainSplinePoint Point;

					// Parse position
					const TArray<TSharedPtr<FJsonValue>>* PosArray;
					if (PointObj->TryGetArrayField(TEXT("position"), PosArray) && PosArray->Num() >= 3)
					{
						Point.Position.X = (*PosArray)[0]->AsNumber();
						Point.Position.Y = (*PosArray)[1]->AsNumber();
						Point.Position.Z = (*PosArray)[2]->AsNumber();
					}

					PowerLine.CablePoints.Add(Point);
				}
			}

			// Parse tower positions
			const TArray<TSharedPtr<FJsonValue>>* TowerPositionsArray;
			if (PowerLineObj->TryGetArrayField(TEXT("tower_positions"), TowerPositionsArray))
			{
				for (const TSharedPtr<FJsonValue>& TowerValue : *TowerPositionsArray)
				{
					const TArray<TSharedPtr<FJsonValue>>* TowerPosArray = &TowerValue->AsArray();
					if (TowerPosArray->Num() >= 3)
					{
						FVector TowerPos;
						TowerPos.X = (*TowerPosArray)[0]->AsNumber();
						TowerPos.Y = (*TowerPosArray)[1]->AsNumber();
						TowerPos.Z = (*TowerPosArray)[2]->AsNumber();
						PowerLine.TowerPositions.Add(TowerPos);
					}
				}
			}

			// Calculate tangents for cable sag
			CalculateSplineTangents(PowerLine.CablePoints);

			OutPowerLines.Add(PowerLine);
		}
	}

	return true;
}

USplineComponent* URealTerrainOSMSplineImporter::CreateSplineComponent(AActor* Owner, const TArray<FRealTerrainSplinePoint>& Points)
{
	if (!Owner || Points.Num() < 2)
	{
		return nullptr;
	}

	// Create spline component
	USplineComponent* SplineComp = NewObject<USplineComponent>(Owner, USplineComponent::StaticClass(), TEXT("SplinePath"));
	if (!SplineComp)
	{
		return nullptr;
	}

	SplineComp->SetupAttachment(Owner->GetRootComponent());
	SplineComp->RegisterComponent();

	// Clear default points
	SplineComp->ClearSplinePoints();

	// Add spline points
	for (int32 i = 0; i < Points.Num(); i++)
	{
		const FRealTerrainSplinePoint& Point = Points[i];

		SplineComp->AddSplinePoint(Point.Position, ESplineCoordinateSpace::World, false);

		// Set tangents
		SplineComp->SetTangentsAtSplinePoint(i, Point.ArriveTangent, Point.LeaveTangent, ESplineCoordinateSpace::World, false);

		// Set scale
		SplineComp->SetSplinePointType(i, ESplinePointType::Curve, false);
	}

	// Update spline
	SplineComp->UpdateSpline();

	return SplineComp;
}

void URealTerrainOSMSplineImporter::CalculateSplineTangents(TArray<FRealTerrainSplinePoint>& Points)
{
	if (Points.Num() < 2)
	{
		return;
	}

	for (int32 i = 0; i < Points.Num(); i++)
	{
		FVector Tangent;

		if (i == 0)
		{
			// First point: tangent toward next point
			Tangent = (Points[i + 1].Position - Points[i].Position).GetSafeNormal();
		}
		else if (i == Points.Num() - 1)
		{
			// Last point: tangent from previous point
			Tangent = (Points[i].Position - Points[i - 1].Position).GetSafeNormal();
		}
		else
		{
			// Middle points: average of incoming and outgoing
			FVector Incoming = (Points[i].Position - Points[i - 1].Position).GetSafeNormal();
			FVector Outgoing = (Points[i + 1].Position - Points[i].Position).GetSafeNormal();
			Tangent = (Incoming + Outgoing).GetSafeNormal();
		}

		// Scale tangent for smoothness (use distance to next point)
		float TangentLength = 100.0f; // Default length
		if (i < Points.Num() - 1)
		{
			TangentLength = FVector::Dist(Points[i].Position, Points[i + 1].Position) * 0.5f;
		}

		Tangent *= TangentLength;

		Points[i].ArriveTangent = Tangent;
		Points[i].LeaveTangent = Tangent;
	}
}
