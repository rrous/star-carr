"""
Star Carr Mesolithic Scholar Simulator - FastAPI Server
With Rule Engine and Upstash Redis state persistence
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import numpy as np
import os

from engine.terrain_generator import (
    load_terrain_rules, generate_terrain, get_terrain_config
)
from engine.species_generator import (
    load_species_rules, generate_species, build_species_database
)
from engine.state_manager import state_manager

app = FastAPI(title="Star Carr Mesolithic Scholar Simulator")

# Global state
terrain_data = None
species_data = None
terrain_types = None
species_database = None
config = None
VISIBILITY_RADIUS = 3


def initialize_world():
    """Initialize world state from Redis or generate from rules."""
    global terrain_data, species_data, terrain_types, species_database, config
    
    # Load rules
    terrain_rules = load_terrain_rules()
    species_rules = load_species_rules()
    
    # Build config and databases
    config = get_terrain_config(terrain_rules)
    config['visibility_radius'] = VISIBILITY_RADIUS
    terrain_types = terrain_rules['terrain_types']
    species_database = build_species_database(species_rules)
    
    # Try to load from Redis first
    if state_manager.has_world_state():
        print("Loading world state from Redis...")
        terrain_data = state_manager.load_terrain()
        species_data = state_manager.load_species()
        
        if terrain_data is not None and species_data is not None:
            print(f"Loaded terrain: {terrain_data.shape}, species: {species_data.shape}")
            return
        else:
            print("Failed to load from Redis, regenerating...")
    
    # Generate from rules
    print("Generating world from rules...")
    terrain_data, _ = generate_terrain(terrain_rules)
    species_data = generate_species(
        terrain_data,
        species_database,
        terrain_types,
        density=species_rules['settings']['density'],
        abundance_weights=species_rules['abundance_weights']
    )
    
    print(f"Generated terrain: {terrain_data.shape}, species: {species_data.shape}")
    
    # Save to Redis
    if state_manager.enabled:
        print("Saving world state to Redis...")
        state_manager.save_terrain(terrain_data)
        state_manager.save_species(species_data)
        state_manager.save_game_state({
            'month': 3,  # March (spring)
            'season': 'spring',
            'year': 9000  # BCE
        })
        print("World state saved to Redis")


# Initialize on startup
initialize_world()


# API Routes

@app.get("/api/config")
def get_config():
    """Return grid configuration and game settings."""
    return config


@app.get("/api/terrain/{x}/{y}")
def get_terrain(x: int, y: int):
    """Return terrain type for specific cell."""
    if not (0 <= x < config['grid_cols'] and 0 <= y < config['grid_rows']):
        raise HTTPException(status_code=404, detail="Cell out of bounds")
    
    terrain_id = int(terrain_data[y, x])
    terrain_info = config['terrain_types'].get(terrain_id, {
        'name': 'unknown', 'color': '#888', 'description': 'Unknown terrain'
    })
    
    return {
        'x': x,
        'y': y,
        'terrain_id': terrain_id,
        'terrain': terrain_info
    }


@app.get("/api/observe/{x}/{y}")
def observe(x: int, y: int):
    """Primary observation endpoint - returns visible species within radius."""
    if not (0 <= x < config['grid_cols'] and 0 <= y < config['grid_rows']):
        raise HTTPException(status_code=404, detail="Cell out of bounds")
    
    # Current terrain
    current_terrain_id = int(terrain_data[y, x])
    current_terrain = config['terrain_types'].get(current_terrain_id, {
        'name': 'unknown', 'description': 'Unknown'
    })
    
    # Collect visible cells and species
    visible_terrains = set()
    observed_species = {}
    
    for dy in range(-VISIBILITY_RADIUS, VISIBILITY_RADIUS + 1):
        for dx in range(-VISIBILITY_RADIUS, VISIBILITY_RADIUS + 1):
            # Check circular radius
            if dx*dx + dy*dy > VISIBILITY_RADIUS * VISIBILITY_RADIUS:
                continue
            
            cx, cy = x + dx, y + dy
            if not (0 <= cx < config['grid_cols'] and 0 <= cy < config['grid_rows']):
                continue
            
            # Track visible terrain
            t_id = int(terrain_data[cy, cx])
            visible_terrains.add(t_id)
            
            # Check for species
            sp_id = int(species_data[cy, cx])
            if sp_id > 0 and sp_id in species_database:
                if sp_id not in observed_species:
                    observed_species[sp_id] = {
                        'species': species_database[sp_id],
                        'count': 0,
                        'locations': []
                    }
                observed_species[sp_id]['count'] += 1
                observed_species[sp_id]['locations'].append({'x': cx, 'y': cy})
    
    # Format terrain list
    terrain_list = []
    for t_id in sorted(visible_terrains):
        t_info = config['terrain_types'].get(t_id, {
            'name': 'unknown', 'color': '#888', 'description': 'Unknown'
        })
        terrain_list.append({'id': t_id, **t_info})
    
    # Format species observations
    species_list = []
    for sp_id, data in observed_species.items():
        sp = data['species']
        species_list.append({
            'id': sp_id,
            'common_name': sp['common_name'],
            'latin_name': sp['latin_name'],
            'category': sp['category'],
            'count': data['count'],
            'visual': sp['visual'],
            'tactile': sp['tactile'],
            'smell': sp['smell'],
            'sound': sp['sound'],
            'habitat': sp['habitat'],
            'season_note': sp['season_note'],
            'uses': sp['uses'],
            'photo_url': sp.get('photo_url')
        })
    
    # Sort by category then name
    category_order = ['tree', 'shrub', 'plant', 'large_herbivore', 'medium_herbivore', 'predator', 'aquatic', 'bird']
    species_list.sort(key=lambda s: (
        category_order.index(s['category']) if s['category'] in category_order else 99,
        s['common_name']
    ))
    
    return {
        'location': {'x': x, 'y': y},
        'current_terrain': {'id': current_terrain_id, **current_terrain},
        'visible_terrains': terrain_list,
        'observations': species_list,
        'observation_count': len(species_list)
    }


@app.get("/api/species")
def get_all_species():
    """Return complete species database."""
    return species_database


@app.get("/api/species/{species_id}")
def get_species(species_id: int):
    """Return detailed info for one species."""
    if species_id not in species_database:
        raise HTTPException(status_code=404, detail="Species not found")
    return species_database[species_id]


@app.get("/api/terrain_batch")
def get_terrain_batch(min_x: int, min_y: int, max_x: int, max_y: int):
    """Return terrain data for a rectangular region."""
    min_x = max(0, min_x)
    min_y = max(0, min_y)
    max_x = min(config['grid_cols'], max_x)
    max_y = min(config['grid_rows'], max_y)
    
    cells = []
    for y in range(min_y, max_y):
        row = []
        for x in range(min_x, max_x):
            row.append(int(terrain_data[y, x]))
        cells.append(row)
    
    return {
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y,
        'cells': cells
    }


@app.get("/api/game_state")
def get_game_state():
    """Return current game state (month, season, etc.)."""
    state = state_manager.load_game_state()
    if state:
        return state
    return {
        'month': 3,
        'season': 'spring',
        'year': 9000
    }


@app.post("/api/regenerate")
def regenerate_world():
    """Regenerate world from rules (admin endpoint)."""
    initialize_world()
    return {'status': 'ok', 'message': 'World regenerated'}


# Static files
os.makedirs("static", exist_ok=True)
os.makedirs("assets/species", exist_ok=True)


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
