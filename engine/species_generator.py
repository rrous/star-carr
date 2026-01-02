"""
Species Generator - Parses species_init.yaml and generates species placement
"""

import numpy as np
import yaml
from pathlib import Path


def load_species_rules(rules_path: str = "rules/species_init.yaml") -> dict:
    """Load species rules from YAML file."""
    with open(rules_path, 'r') as f:
        return yaml.safe_load(f)


def build_species_database(rules: dict) -> dict:
    """Convert YAML species to database format (keyed by ID)."""
    database = {}
    default_photo = rules['settings'].get('default_photo', '/assets/species/placeholder.png')
    
    for name, data in rules['species'].items():
        species_id = data['id']
        obs = data.get('observations', {})
        
        database[species_id] = {
            'id': species_id,
            'common_name': name.replace('_', ' ').title(),
            'latin_name': data['latin'],
            'category': data['category'],
            'abundance': data['abundance'],
            'terrain_preference': data['terrains'],  # Keep as names for now
            'photo_url': data.get('photo', default_photo),
            'visual': obs.get('visual', ''),
            'tactile': obs.get('tactile', ''),
            'smell': obs.get('smell', ''),
            'sound': obs.get('sound', ''),
            'habitat': obs.get('habitat', ''),
            'season_note': obs.get('season', ''),
            'uses': obs.get('uses', '')
        }
    
    return database


def get_terrain_name_to_id(terrain_types: dict) -> dict:
    """Build terrain name to ID mapping."""
    return {name: info['id'] for name, info in terrain_types.items()}


def get_species_for_terrain(species_db: dict, terrain_name: str) -> list:
    """Return list of species IDs that can appear in given terrain."""
    suitable = []
    for species_id, data in species_db.items():
        if terrain_name in data['terrain_preference']:
            suitable.append(species_id)
    return suitable


def generate_species(
    terrain: np.ndarray,
    species_db: dict,
    terrain_types: dict,
    density: float = 0.3,
    abundance_weights: dict = None
) -> np.ndarray:
    """
    Generate species placement array based on terrain and rules.
    Returns array where 0 = no species, otherwise species ID.
    """
    if abundance_weights is None:
        abundance_weights = {
            'abundant': 5,
            'very_common': 4,
            'common': 3,
            'occasional': 2,
            'rare': 1,
            'very_rare': 0.5
        }
    
    rows, cols = terrain.shape
    species = np.zeros((rows, cols), dtype=np.uint8)
    
    # Build terrain ID to name mapping
    id_to_name = {info['id']: name for name, info in terrain_types.items()}
    
    # Pre-compute species lists for each terrain type
    terrain_species = {}
    for name in terrain_types.keys():
        terrain_species[name] = get_species_for_terrain(species_db, name)
    
    for y in range(rows):
        for x in range(cols):
            # Only populate some cells
            if np.random.random() > density:
                continue
            
            terrain_id = terrain[y, x]
            terrain_name = id_to_name.get(terrain_id)
            
            if not terrain_name:
                continue
                
            suitable = terrain_species.get(terrain_name, [])
            
            if not suitable:
                continue
            
            # Weight by abundance
            weights = []
            for sp_id in suitable:
                abundance = species_db[sp_id].get('abundance', 'common')
                weights.append(abundance_weights.get(abundance, 1))
            
            # Normalize weights
            total = sum(weights)
            if total > 0:
                weights = [w / total for w in weights]
                species[y, x] = np.random.choice(suitable, p=weights)
    
    return species


def get_species_config(rules: dict) -> dict:
    """Extract species settings for API."""
    return {
        'density': rules['settings']['density'],
        'season': rules['settings']['season'],
        'default_photo': rules['settings'].get('default_photo', '/assets/species/placeholder.png')
    }


if __name__ == "__main__":
    # Test
    from terrain_generator import load_terrain_rules, generate_terrain
    
    terrain_rules = load_terrain_rules()
    terrain, terrain_types = generate_terrain(terrain_rules)
    
    species_rules = load_species_rules()
    species_db = build_species_database(species_rules)
    
    species = generate_species(
        terrain,
        species_db,
        terrain_types,
        density=species_rules['settings']['density'],
        abundance_weights=species_rules['abundance_weights']
    )
    
    print(f"Generated species: {species.shape}")
    cells_with_species = np.count_nonzero(species)
    print(f"Cells with species: {cells_with_species:,} ({100*cells_with_species/species.size:.1f}%)")
