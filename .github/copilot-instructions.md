# AI Coding Assistant Instructions for Star Carr Mesolithic Simulator

## Project Overview
This is a FastAPI-based web simulation of Mesolithic-era Star Carr (9000 BCE), featuring procedural world generation from YAML configuration files. The system generates terrain, places species with realistic ecological interactions, and provides an observation interface for "scholars" exploring the landscape.

## Architecture
- **Backend**: FastAPI server (`main.py`) with REST API endpoints
- **World Generation**: Rule-based system using YAML configs (`rules/`) parsed by engine modules (`engine/`)
- **Persistence**: Upstash Redis for cloud deployment, local numpy files for development
- **Frontend**: Vanilla JS/HTML/CSS map interface (`static/`)
- **Tools**: Image download utilities (`tools/`) for species photos

## Key Components
- `engine/terrain_generator.py`: Procedural terrain from lake-based zones + corridors
- `engine/species_generator.py`: Species placement with effects (exclusion, damage, signs)
- `engine/state_manager.py`: Observation logic, persistence, conditional text evaluation
- `rules/terrain_init.yaml`: Terrain types, lake zones, corridor definitions
- `rules/species_init.yaml`: Species distributions, effects, observation texts

## Critical Patterns

### YAML Configuration Structure
```yaml
species:
  birch:
    id: 1
    category: tree
    distribution:
      terrain_weights: {birch_woodland: 1.0, grassland: 0.2}
      clustering: {type: stand, stand_radius: [5,15]}
    effects:
      - effect: damages
        targets: {tag: softwood}
        params: {radius: 10, state_definition: tree_damage}
    observation:
      visual: "Description text"
      conditional_texts:
        - condition: "self.state == 2"
          append_to: visual
          text: "Additional text when damaged"
```

### Spatial Data Handling
- Use numpy arrays for terrain/species grids (rows, cols)
- Terrain: uint8 IDs, Species presence: uint8 arrays
- Base64 encoding for Redis storage: `np_to_b64(arr)` / `b64_to_np(s, dtype, shape)`

### Observation System
- Context evaluation with dot notation: `species.beaver.present`, `terrain.current == "grassland"`
- Conditional text appending based on conditions
- Distance calculations for nearby species/signs

### Effects System
- **excludes**: Reduces target species probability in radius
- **damages**: Applies state transitions (healthy → gnawed → felled)
- **creates_sign**: Places track/scat symbols on terrain
- **promotes**: Increases target density

## Development Workflow

### Local Development
```bash
pip install -r requirements.txt
python main.py
# Access http://localhost:8000
```

### Rule Editing
1. Edit `rules/*.yaml` files
2. Push to GitHub → Render auto-deploys
3. Call `POST /api/regenerate` to rebuild world
4. Or clear Redis via Upstash console

### Environment Setup
- **Redis**: Set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
- **Render**: Environment variables in dashboard
- **Local**: Falls back to `data/` directory with numpy files

## Code Conventions

### Species Categories
- `tree`/`shrub`/`plant`: Vegetation with clustering (stand/clump/continuous)
- `large_herbivore`/`medium_herbivore`: Animals with group_size/spread
- `predator`: Low presence probability, exclusion effects
- `aquatic`: Water-adjacent placement

### Terrain Integration
- Terrain IDs: 0=deep_water, 1=shallow_water, 2=reed_bed, etc.
- Corridors: `water_edge`, `ecotone`, `game_trail` influence placement
- Distance transforms for water proximity limits

### State Management
- Load/generate pattern: Check Redis → local files → generate new
- Base64 numpy serialization for cloud persistence
- Context building for conditional observations

## Common Tasks

### Adding New Species
1. Add entry to `rules/species_init.yaml` with id, category, distribution
2. Define terrain_weights and clustering parameters
3. Add observation texts with conditionals
4. Optionally add effects (exclusion zones, damage states)

### Modifying Terrain
1. Update `rules/terrain_init.yaml` terrain_types or lake zones
2. Adjust corridor definitions if needed
3. Regenerate world via API

### Adding Effects
- Use `targets: {tag: wolf_prey}` or `targets: {category: predator}`
- Radius/probability parameters control influence
- State definitions in `state_definitions` section

## Debugging
- Check `/api/config` for grid/terrain setup
- Use `/api/god_mode/corridors` and `/api/god_mode/signs` for visualization
- Redis keys: `star_carr:world` contains full state
- Local files: `data/terrain.npy`, `data/species_*.npy`

## Deployment
- **Render**: Auto-deploys on GitHub push
- **Redis**: Upstash for persistence across restarts
- **Assets**: Species images in `assets/species/` served statically