"""
Star Carr Data Generator
Generates synthetic terrain and species distribution data for the prototype.
"""

import numpy as np
import os
from config import (
    GRID_COLS, GRID_ROWS, SPAWN_X, SPAWN_Y,
    SPECIES_DENSITY, SPECIES_DATABASE, get_species_for_terrain
)

def generate_terrain():
    """Generate terrain map with lake in center-east, woodland around edges."""
    terrain = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.uint8)
    
    # Lake center (ellipse in center-east of map)
    lake_center_x = 120
    lake_center_y = 125
    lake_radius_x = 60
    lake_radius_y = 80
    
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            # Distance from lake center (elliptical)
            dx = (x - lake_center_x) / lake_radius_x
            dy = (y - lake_center_y) / lake_radius_y
            dist = np.sqrt(dx*dx + dy*dy)
            
            # Add some noise for irregular edges
            noise = np.random.uniform(-0.15, 0.15)
            dist += noise
            
            if dist < 0.5:
                terrain[y, x] = 0  # deep_water
            elif dist < 0.7:
                terrain[y, x] = 1  # shallow_water
            elif dist < 0.85:
                terrain[y, x] = 2  # reed_bed
            elif dist < 1.0:
                terrain[y, x] = 3  # wetland
            elif dist < 1.2:
                terrain[y, x] = 4  # carr_woodland
            elif dist < 1.5:
                # Mix of birch and mixed woodland
                terrain[y, x] = 5 if np.random.random() > 0.4 else 6
            else:
                # Outer areas: mix of woodland and grassland
                r = np.random.random()
                if r < 0.3:
                    terrain[y, x] = 7  # grassland
                elif r < 0.6:
                    terrain[y, x] = 5  # birch_woodland
                else:
                    terrain[y, x] = 6  # mixed_woodland
    
    # Place platform at spawn location
    terrain[SPAWN_Y, SPAWN_X] = 8
    # Make platform area slightly larger (3x3)
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            py, px = SPAWN_Y + dy, SPAWN_X + dx
            if 0 <= py < GRID_ROWS and 0 <= px < GRID_COLS:
                terrain[py, px] = 8
    
    # Add some grassland patches in southwest
    for _ in range(5):
        cx = np.random.randint(10, 50)
        cy = np.random.randint(180, 240)
        radius = np.random.randint(5, 15)
        for y in range(max(0, cy-radius), min(GRID_ROWS, cy+radius)):
            for x in range(max(0, cx-radius), min(GRID_COLS, cx+radius)):
                if (x-cx)**2 + (y-cy)**2 < radius**2:
                    if terrain[y, x] not in [0, 1, 2, 8]:  # Don't overwrite water or platform
                        terrain[y, x] = 7  # grassland
    
    return terrain


def generate_species(terrain):
    """Generate species presence map based on terrain preferences."""
    # 0 = no notable species, otherwise species ID
    species = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.uint8)
    
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            # Only populate some cells
            if np.random.random() > SPECIES_DENSITY:
                continue
            
            terrain_type = terrain[y, x]
            suitable_species = get_species_for_terrain(terrain_type)
            
            if suitable_species:
                # Weight by abundance
                weights = []
                for sp_id in suitable_species:
                    abundance = SPECIES_DATABASE[sp_id].get("abundance", "common")
                    weight_map = {
                        "abundant": 5,
                        "very_common": 4,
                        "common": 3,
                        "occasional": 2,
                        "rare": 1,
                        "very_rare": 0.5
                    }
                    weights.append(weight_map.get(abundance, 1))
                
                # Normalize weights
                total = sum(weights)
                weights = [w/total for w in weights]
                
                # Select species
                species[y, x] = np.random.choice(suitable_species, p=weights)
    
    return species


def main():
    """Generate and save all data files."""
    print("Generating Star Carr data...")
    
    # Create data directories
    os.makedirs("data/raster", exist_ok=True)
    os.makedirs("data/vector", exist_ok=True)
    
    # Generate terrain
    print("  Generating terrain...")
    terrain = generate_terrain()
    np.save("data/raster/terrain_type.npy", terrain)
    print(f"    Saved terrain_type.npy ({terrain.shape})")
    
    # Print terrain distribution
    unique, counts = np.unique(terrain, return_counts=True)
    print("    Terrain distribution:")
    for t, c in zip(unique, counts):
        pct = 100 * c / terrain.size
        print(f"      {t}: {c:,} cells ({pct:.1f}%)")
    
    # Generate species
    print("  Generating species distribution...")
    species = generate_species(terrain)
    np.save("data/raster/species_presence.npy", species)
    print(f"    Saved species_presence.npy ({species.shape})")
    
    # Count species occurrences
    cells_with_species = np.count_nonzero(species)
    print(f"    Cells with species: {cells_with_species:,} ({100*cells_with_species/species.size:.1f}%)")
    
    # Create simple GeoJSON for platform
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Star Carr Platform", "type": "platform"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [SPAWN_X, SPAWN_Y]
                }
            }
        ]
    }
    
    import json
    with open("data/vector/features.geojson", "w") as f:
        json.dump(geojson, f, indent=2)
    print("    Saved features.geojson")
    
    # Export species database as JSON for frontend
    with open("data/species.json", "w") as f:
        json.dump(SPECIES_DATABASE, f, indent=2)
    print("    Saved species.json")
    
    print("\nData generation complete!")
    print(f"Platform location: ({SPAWN_X}, {SPAWN_Y})")


if __name__ == "__main__":
    main()
