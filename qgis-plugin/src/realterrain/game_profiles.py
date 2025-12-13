"""
Game Profile Configuration System

This module defines different game profile presets that auto-configure
the plugin settings based on the user's project type.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class GameProfile:
    """Represents a game profile with all configuration settings."""

    id: str
    name: str
    description: str
    icon: str
    category: str  # "game" or "non_game"
    examples: List[str]

    # Data source settings
    elevation_enabled: bool = True
    elevation_resolution: int = 10  # meters
    elevation_source: str = "srtm"

    satellite_enabled: bool = True
    satellite_resolution: int = 2  # meters
    satellite_prefer_recent: bool = False

    osm_enabled: bool = True
    osm_features: List[str] = field(default_factory=lambda: ["roads", "buildings", "water"])

    # Material settings
    materials_enabled: bool = True
    material_types: List[str] = field(default_factory=lambda: ["grass", "dirt", "rock", "forest"])

    # Special features
    tactical_analysis: bool = False
    fortifications_enabled: bool = False
    fortification_level: str = "medium"  # light/medium/heavy/extreme
    fortification_types: List[str] = field(default_factory=list)

    cover_analysis: bool = False
    spawn_points_enabled: bool = False
    navmesh_hints: bool = False

    seasonal_variations: bool = False
    vegetation_distribution: bool = False
    trail_generation: bool = False
    poi_suggestions: bool = False
    biome_transitions: bool = False

    procedural_buildings_enabled: bool = False
    procedural_building_style: str = "regional"
    procedural_building_density: str = "medium"

    scatter_objects_enabled: bool = False
    scatter_object_types: List[str] = field(default_factory=list)

    road_network_enhancement: bool = False
    racing_track_analysis: bool = False

    # Optimization
    collision_mesh: str = "medium"  # low/medium/detailed/road_optimized
    lod_levels: int = 3

    # Tips for the user
    tips: List[str] = field(default_factory=list)

    # UE5 recommendations
    ue5_landscape_material: str = "Default_Master"
    ue5_collision: str = "Medium_Detail"
    ue5_streaming: str = "World_Partition"


# Define all game profiles
PROFILES: Dict[str, GameProfile] = {
    "military_simulation": GameProfile(
        id="military_simulation",
        name="Military Simulation / Tactical Shooter",
        description="Realistic terrain for tactical games",
        icon="🎖️",
        category="game",
        examples=["Arma", "Squad", "Ground Branch", "Insurgency"],

        elevation_resolution=5,
        elevation_source="best_available",
        satellite_resolution=1,
        satellite_prefer_recent=True,

        osm_features=["roads", "buildings", "railways", "power_lines", "fences", "bridges"],
        material_types=["grass", "dirt", "rock", "forest", "sand", "gravel"],

        tactical_analysis=True,
        fortifications_enabled=True,
        fortification_level="medium",
        fortification_types=[
            "hesco_barriers", "sandbags", "trenches",
            "roadblocks", "speed_bumps", "wire_obstacles"
        ],
        cover_analysis=True,
        spawn_points_enabled=True,
        navmesh_hints=True,

        collision_mesh="detailed",
        lod_levels=4,

        tips=[
            "✅ Tactical analysis enabled - AI will suggest defensive positions",
            "✅ Fortifications will be auto-placed at strategic points",
            "✅ Cover analysis will mark bullet-stopping objects",
            "💡 Recommended: Use 'medium' fortification level for balanced gameplay",
            "💡 Check spawn point suggestions in tactical_data.json after export"
        ],

        ue5_landscape_material="Military_Master",
        ue5_collision="High_Detail",
    ),

    "open_world": GameProfile(
        id="open_world",
        name="Open World / RPG",
        description="Vast explorable worlds with diverse biomes",
        icon="🗺️",
        category="game",
        examples=["Skyrim", "Witcher", "GTA", "RDR2"],

        elevation_resolution=10,
        satellite_resolution=2,

        osm_features=["roads", "buildings", "water", "forests", "landmarks"],
        material_types=["grass", "dirt", "rock", "forest", "snow", "sand", "water"],

        seasonal_variations=True,
        vegetation_distribution=True,
        trail_generation=True,
        poi_suggestions=True,
        biome_transitions=True,

        procedural_buildings_enabled=True,
        procedural_building_style="regional",
        procedural_building_density="medium",

        scatter_objects_enabled=True,
        scatter_object_types=["rocks", "logs", "flowers", "bushes"],

        tips=[
            "✅ Seasonal variations enabled - 4 versions of terrain",
            "✅ Trail network will connect interesting locations",
            "✅ Biome transitions will blend naturally",
            "💡 Consider using 'vibrant' color grading for fantasy feel",
            "💡 POI suggestions will mark scenic viewpoints and quest locations"
        ],
    ),

    "racing": GameProfile(
        id="racing",
        name="Racing / Driving Game",
        description="Optimized road networks and race tracks",
        icon="🏎️",
        category="game",
        examples=["Forza Horizon", "Gran Turismo", "Need for Speed"],

        elevation_resolution=5,
        satellite_resolution=1,

        osm_features=["roads", "highways", "tracks", "buildings", "landmarks"],
        material_types=["asphalt", "dirt", "gravel", "grass", "concrete"],

        road_network_enhancement=True,
        racing_track_analysis=True,

        collision_mesh="road_optimized",

        procedural_buildings_enabled=True,

        tips=[
            "✅ Road network enhanced with proper width and markings",
            "✅ Corner analysis will rate difficulty of turns",
            "✅ Track suggestions for point-to-point and circuit races",
            "💡 Guard rails auto-placed on dangerous curves",
            "💡 Check racing_analysis.json for lap time estimates"
        ],
    ),

    "survival": GameProfile(
        id="survival",
        name="Survival / Crafting",
        description="Resource-rich environments for survival games",
        icon="⛺",
        category="game",
        examples=["Rust", "DayZ", "The Forest", "Minecraft-like"],

        elevation_resolution=10,
        satellite_resolution=2,

        osm_features=["roads", "buildings", "water", "forests"],
        material_types=["grass", "dirt", "rock", "forest", "sand", "snow", "water"],

        vegetation_distribution=True,
        poi_suggestions=True,

        procedural_buildings_enabled=True,
        procedural_building_density="low",

        scatter_objects_enabled=True,
        scatter_object_types=["rocks", "logs", "bushes", "debris"],

        tips=[
            "✅ Vegetation distribution for resource gathering areas",
            "✅ POI suggestions for camps and shelters",
            "💡 Scattered objects provide cover and resources",
            "💡 Buildings sparsely placed for exploration"
        ],
    ),

    "flight_simulator": GameProfile(
        id="flight_simulator",
        name="Flight Simulator",
        description="Wide-area terrain for aviation",
        icon="✈️",
        category="game",
        examples=["MSFS", "X-Plane", "DCS"],

        elevation_resolution=30,  # Larger areas, lower detail
        satellite_resolution=10,

        osm_features=["airports", "roads", "water", "landmarks"],
        material_types=["grass", "water", "urban", "forest"],

        tips=[
            "✅ Optimized for large area coverage",
            "✅ Airports and landmarks included",
            "💡 Use lower resolution for better performance over vast areas",
            "💡 Focus on distinctive terrain features for navigation"
        ],
    ),

    "battle_royale": GameProfile(
        id="battle_royale",
        name="Battle Royale",
        description="Balanced combat arenas with strategic locations",
        icon="🎯",
        category="game",
        examples=["PUBG", "Fortnite", "Apex Legends"],

        elevation_resolution=5,
        satellite_resolution=1,

        osm_features=["roads", "buildings", "water"],
        material_types=["grass", "dirt", "rock", "urban", "sand"],

        cover_analysis=True,
        spawn_points_enabled=True,
        poi_suggestions=True,

        procedural_buildings_enabled=True,
        procedural_building_density="high",

        tips=[
            "✅ Cover analysis for balanced combat",
            "✅ Spawn points distributed fairly",
            "✅ POI suggestions for hot zones",
            "💡 Buildings provide vertical gameplay opportunities"
        ],
    ),

    "city_builder": GameProfile(
        id="city_builder",
        name="City Builder / Strategy",
        description="Detailed urban and regional planning",
        icon="🏙️",
        category="game",
        examples=["Cities Skylines", "Anno", "Civilization"],

        elevation_resolution=10,
        satellite_resolution=2,

        osm_features=["roads", "buildings", "water", "railways", "power_lines"],
        material_types=["urban", "grass", "water", "industrial"],

        road_network_enhancement=True,
        procedural_buildings_enabled=True,
        procedural_building_density="high",

        tips=[
            "✅ Complete road network with proper hierarchy",
            "✅ Building footprints for urban planning",
            "💡 Use existing infrastructure as starting point",
            "💡 Water features important for city layout"
        ],
    ),

    "horror": GameProfile(
        id="horror",
        name="Horror / Atmospheric",
        description="Eerie environments with dense detail",
        icon="👻",
        category="game",
        examples=["Silent Hill", "Resident Evil", "Outlast"],

        elevation_resolution=5,
        satellite_resolution=1,

        osm_features=["roads", "buildings", "forests", "abandoned_structures"],
        material_types=["dirt", "rock", "forest", "urban", "overgrown"],

        vegetation_distribution=True,
        procedural_buildings_enabled=True,
        procedural_building_density="low",

        scatter_objects_enabled=True,
        scatter_object_types=["debris", "logs", "rocks"],

        tips=[
            "✅ Dense vegetation for atmosphere",
            "✅ Isolated buildings for tension",
            "💡 Overgrown materials create abandonment feel",
            "💡 Use fog and darkness to enhance terrain"
        ],
    ),

    "multiplayer_shooter": GameProfile(
        id="multiplayer_shooter",
        name="Multiplayer Shooter (Non-tactical)",
        description="Fast-paced combat environments",
        icon="🔫",
        category="game",
        examples=["Battlefield", "Call of Duty", "Halo"],

        elevation_resolution=5,
        satellite_resolution=1,

        osm_features=["roads", "buildings", "urban_features"],
        material_types=["urban", "grass", "dirt", "concrete"],

        cover_analysis=True,
        spawn_points_enabled=True,

        procedural_buildings_enabled=True,
        procedural_building_density="medium",

        collision_mesh="detailed",

        tips=[
            "✅ Cover analysis for balanced gunplay",
            "✅ Spawn points for team balance",
            "💡 Focus on medium-range engagement distances",
            "💡 Urban areas provide multi-level combat"
        ],
    ),

    "architectural_viz": GameProfile(
        id="architectural_viz",
        name="Architectural Visualization",
        description="High-fidelity real estate and urban planning",
        icon="🏗️",
        category="non_game",
        examples=["Real estate", "Urban planning", "Presentations"],

        elevation_resolution=1,  # Highest detail
        satellite_resolution=0.5,
        satellite_prefer_recent=True,

        osm_features=["roads", "buildings", "landmarks", "vegetation"],
        material_types=["concrete", "asphalt", "grass", "urban"],

        procedural_buildings_enabled=False,  # Use real buildings

        tips=[
            "✅ Maximum detail for photorealism",
            "✅ Recent satellite imagery",
            "💡 Use real building footprints, not procedural",
            "💡 Import CAD models for hero buildings"
        ],
    ),

    "film_production": GameProfile(
        id="film_production",
        name="Film / Virtual Production",
        description="Background plates and previsualization",
        icon="🎬",
        category="non_game",
        examples=["Background plates", "Previsualization", "LED walls"],

        elevation_resolution=5,
        satellite_resolution=1,
        satellite_prefer_recent=True,

        osm_features=["roads", "buildings", "landmarks", "water"],
        material_types=["realistic_all"],

        tips=[
            "✅ High quality for close-up shots",
            "✅ Recent imagery for accuracy",
            "💡 Consider time of day and seasons",
            "💡 Export camera paths separately"
        ],
    ),

    "education": GameProfile(
        id="education",
        name="Education / Research",
        description="Geographic and scientific visualization",
        icon="🎓",
        category="non_game",
        examples=["Geography", "Geology", "Simulation", "Teaching"],

        elevation_resolution=30,
        satellite_resolution=10,

        osm_features=["roads", "water", "landmarks", "boundaries"],
        material_types=["educational"],

        tips=[
            "✅ Balanced detail and performance",
            "✅ Suitable for analysis and demonstration",
            "💡 Focus on accuracy over aesthetics",
            "💡 Export metadata for scientific use"
        ],
    ),

    "custom": GameProfile(
        id="custom",
        name="Custom / Advanced",
        description="Full manual control for power users",
        icon="🔧",
        category="non_game",
        examples=["Custom projects", "Experimental", "Advanced users"],

        elevation_resolution=10,
        satellite_resolution=2,

        tips=[
            "💡 All settings available for manual configuration",
            "💡 No automatic optimizations applied",
            "💡 Recommended for experienced users only"
        ],
    ),
}


def get_profile(profile_id: str) -> GameProfile:
    """Get a game profile by ID."""
    return PROFILES.get(profile_id, PROFILES["custom"])


def get_all_profiles() -> List[GameProfile]:
    """Get all available profiles."""
    return list(PROFILES.values())


def get_profiles_by_category(category: str) -> List[GameProfile]:
    """Get profiles filtered by category ('game' or 'non_game')."""
    return [p for p in PROFILES.values() if p.category == category]
