"""
Star Carr Mesolithic Scholar Simulator - FastAPI Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import numpy as np
import os

from config import (
    GRID_COLS, GRID_ROWS, CELL_SIZE_M, ORIGIN_E, ORIGIN_N,
    SPAWN_X, SPAWN_Y, VISIBILITY_RADIUS,
    TERRAIN_TYPES, SPECIES_DATABASE
)

app = FastAPI(title="Star Carr Mesolithic Scholar Simulator")

# Load data files
terrain_data = None
species_data = None

def load_data():
    global terrain_data, species_data
    try:
        terrain_data = np.load("data/raster/terrain_type.npy")
        species_data = np.load("data/raster/species_presence.npy")
        print(f"Loaded terrain: {terrain_data.shape}, species: {species_data.shape}")
    except FileNotFoundError:
        print("Data files not found. Run generate_data.py first.")
        terrain_data = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.uint8)
        species_data = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.uint8)

load_data()

# API Routes

@app.get("/api/config")
def get_config():
    """Return grid configuration and game settings."""
    return {
        "grid_cols": GRID_COLS,
        "grid_rows": GRID_ROWS,
        "cell_size_m": CELL_SIZE_M,
        "origin_e": ORIGIN_E,
        "origin_n": ORIGIN_N,
        "spawn_x": SPAWN_X,
        "spawn_y": SPAWN_Y,
        "visibility_radius": VISIBILITY_RADIUS,
        "terrain_types": TERRAIN_TYPES
    }


@app.get("/api/terrain/{x}/{y}")
def get_terrain(x: int, y: int):
    """Return terrain type for specific cell."""
    if not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS):
        raise HTTPException(status_code=404, detail="Cell out of bounds")
    
    terrain_id = int(terrain_data[y, x])
    return {
        "x": x,
        "y": y,
        "terrain_id": terrain_id,
        "terrain": TERRAIN_TYPES.get(terrain_id, {"name": "unknown", "color": "#888", "description": "Unknown terrain"})
    }


@app.get("/api/observe/{x}/{y}")
def observe(x: int, y: int):
    """
    Primary observation endpoint.
    Returns all visible species within visibility radius.
    """
    if not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS):
        raise HTTPException(status_code=404, detail="Cell out of bounds")
    
    # Current terrain
    current_terrain_id = int(terrain_data[y, x])
    current_terrain = TERRAIN_TYPES.get(current_terrain_id, {"name": "unknown", "description": "Unknown"})
    
    # Collect visible cells and species
    visible_terrains = set()
    observed_species = {}
    
    for dy in range(-VISIBILITY_RADIUS, VISIBILITY_RADIUS + 1):
        for dx in range(-VISIBILITY_RADIUS, VISIBILITY_RADIUS + 1):
            # Check circular radius
            if dx*dx + dy*dy > VISIBILITY_RADIUS * VISIBILITY_RADIUS:
                continue
            
            cx, cy = x + dx, y + dy
            if not (0 <= cx < GRID_COLS and 0 <= cy < GRID_ROWS):
                continue
            
            # Track visible terrain
            t_id = int(terrain_data[cy, cx])
            visible_terrains.add(t_id)
            
            # Check for species
            sp_id = int(species_data[cy, cx])
            if sp_id > 0 and sp_id in SPECIES_DATABASE:
                if sp_id not in observed_species:
                    observed_species[sp_id] = {
                        "species": SPECIES_DATABASE[sp_id],
                        "count": 0,
                        "locations": []
                    }
                observed_species[sp_id]["count"] += 1
                observed_species[sp_id]["locations"].append({"x": cx, "y": cy})
    
    # Format terrain list
    terrain_list = [
        {"id": t_id, **TERRAIN_TYPES.get(t_id, {"name": "unknown", "color": "#888", "description": "Unknown"})}
        for t_id in sorted(visible_terrains)
    ]
    
    # Format species observations
    species_list = []
    for sp_id, data in observed_species.items():
        sp = data["species"]
        species_list.append({
            "id": sp_id,
            "common_name": sp["common_name"],
            "latin_name": sp["latin_name"],
            "category": sp["category"],
            "count": data["count"],
            "visual": sp["visual"],
            "tactile": sp["tactile"],
            "smell": sp["smell"],
            "sound": sp["sound"],
            "habitat": sp["habitat"],
            "season_note": sp["season_note"],
            "uses": sp["uses"],
            "photo_url": sp.get("photo_url")
        })
    
    # Sort by category then name
    category_order = ["tree", "shrub", "plant", "large_herbivore", "medium_herbivore", "predator", "aquatic"]
    species_list.sort(key=lambda s: (
        category_order.index(s["category"]) if s["category"] in category_order else 99,
        s["common_name"]
    ))
    
    return {
        "location": {"x": x, "y": y},
        "current_terrain": {
            "id": current_terrain_id,
            **current_terrain
        },
        "visible_terrains": terrain_list,
        "observations": species_list,
        "observation_count": len(species_list)
    }


@app.get("/api/species")
def get_all_species():
    """Return complete species database."""
    return SPECIES_DATABASE


@app.get("/api/species/{species_id}")
def get_species(species_id: int):
    """Return detailed info for one species."""
    if species_id not in SPECIES_DATABASE:
        raise HTTPException(status_code=404, detail="Species not found")
    return SPECIES_DATABASE[species_id]


@app.get("/api/terrain_batch")
def get_terrain_batch(min_x: int, min_y: int, max_x: int, max_y: int):
    """Return terrain data for a rectangular region (for map rendering)."""
    # Clamp to valid range
    min_x = max(0, min_x)
    min_y = max(0, min_y)
    max_x = min(GRID_COLS, max_x)
    max_y = min(GRID_ROWS, max_y)
    
    cells = []
    for y in range(min_y, max_y):
        row = []
        for x in range(min_x, max_x):
            row.append(int(terrain_data[y, x]))
        cells.append(row)
    
    return {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "cells": cells
    }


# Static files and frontend
os.makedirs("static", exist_ok=True)

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
