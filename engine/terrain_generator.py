"""
Terrain Generator - Parses terrain_init.yaml and generates terrain array
"""

import numpy as np
import yaml
from pathlib import Path


def load_terrain_rules(rules_path: str = "rules/terrain_init.yaml") -> dict:
    """Load terrain rules from YAML file."""
    with open(rules_path, 'r') as f:
        return yaml.safe_load(f)


def point_in_ellipse(x: int, y: int, center: list, radius: list) -> bool:
    """Check if point is inside ellipse."""
    dx = (x - center[0]) / radius[0]
    dy = (y - center[1]) / radius[1]
    return (dx * dx + dy * dy) <= 1.0


def point_in_rect(x: int, y: int, bounds: list) -> bool:
    """Check if point is inside rectangle. bounds = [x1, y1, x2, y2]"""
    return bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]


def point_in_polygon(x: int, y: int, points: list) -> bool:
    """Check if point is inside polygon using ray casting."""
    n = len(points)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = points[i]
        xj, yj = points[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def generate_terrain(rules: dict) -> tuple[np.ndarray, dict]:
    """
    Generate terrain array from rules.
    Returns (terrain_array, terrain_types_dict)
    """
    grid = rules['grid']
    cols, rows = grid['cols'], grid['rows']
    
    # Build terrain name -> id mapping
    terrain_types = rules['terrain_types']
    name_to_id = {name: info['id'] for name, info in terrain_types.items()}
    
    # Get default terrain
    default_terrain = rules['defaults']['terrain']
    default_id = name_to_id[default_terrain]
    
    # Initialize array with default
    terrain = np.full((rows, cols), default_id, dtype=np.uint8)
    
    # Process zones in order (later overwrites earlier)
    for zone in rules['zones']:
        terrain_name = zone['terrain']
        terrain_id = name_to_id[terrain_name]
        shape = zone['shape']
        
        if shape == 'ellipse':
            center = zone['center']
            radius = zone['radius']
            # Calculate bounding box for efficiency
            min_x = max(0, int(center[0] - radius[0] - 1))
            max_x = min(cols, int(center[0] + radius[0] + 2))
            min_y = max(0, int(center[1] - radius[1] - 1))
            max_y = min(rows, int(center[1] + radius[1] + 2))
            
            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    if point_in_ellipse(x, y, center, radius):
                        terrain[y, x] = terrain_id
                        
        elif shape == 'rect':
            bounds = zone['bounds']
            x1 = max(0, bounds[0])
            y1 = max(0, bounds[1])
            x2 = min(cols, bounds[2] + 1)
            y2 = min(rows, bounds[3] + 1)
            terrain[y1:y2, x1:x2] = terrain_id
            
        elif shape == 'polygon':
            points = zone['points']
            # Calculate bounding box
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            min_x = max(0, min(xs))
            max_x = min(cols, max(xs) + 1)
            min_y = max(0, min(ys))
            max_y = min(rows, max(ys) + 1)
            
            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    if point_in_polygon(x, y, points):
                        terrain[y, x] = terrain_id
    
    return terrain, terrain_types


def get_terrain_config(rules: dict) -> dict:
    """Extract configuration for API responses."""
    grid = rules['grid']
    spawn = rules['spawn']
    terrain_types = rules['terrain_types']
    
    # Convert terrain_types to API format (id as key)
    types_by_id = {}
    for name, info in terrain_types.items():
        types_by_id[info['id']] = {
            'name': name,
            'color': info['color'],
            'description': info['description']
        }
    
    return {
        'grid_cols': grid['cols'],
        'grid_rows': grid['rows'],
        'cell_size_m': grid['cell_size_m'],
        'origin_e': grid['origin_easting'],
        'origin_n': grid['origin_northing'],
        'spawn_x': spawn['x'],
        'spawn_y': spawn['y'],
        'terrain_types': types_by_id
    }


if __name__ == "__main__":
    # Test generation
    rules = load_terrain_rules()
    terrain, types = generate_terrain(rules)
    print(f"Generated terrain: {terrain.shape}")
    
    # Print distribution
    unique, counts = np.unique(terrain, return_counts=True)
    print("\nTerrain distribution:")
    for t, c in zip(unique, counts):
        pct = 100 * c / terrain.size
        print(f"  {t}: {c:,} cells ({pct:.1f}%)")
