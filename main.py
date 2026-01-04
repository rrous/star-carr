"""
Star Carr Mesolithic Scholar Simulator - FastAPI Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yaml
import os

# Load rules
with open('rules/terrain_init.yaml') as f:
    terrain_rules = yaml.safe_load(f)
with open('rules/species_init.yaml') as f:
    species_rules = yaml.safe_load(f)

rules = {'terrain': terrain_rules, 'species': species_rules}

# Initialize state manager
from engine import StateManager
state = StateManager(rules)
state.load_or_generate(seed=42)

app = FastAPI(title="Star Carr Mesolithic Scholar Simulator")


class TimeUpdate(BaseModel):
    time_of_day: str


@app.get("/api/config")
def get_config():
    return state.get_config()


@app.get("/api/terrain/{x}/{y}")
def get_terrain(x: int, y: int):
    cfg = state.get_config()
    if not (0 <= x < cfg['grid_cols'] and 0 <= y < cfg['grid_rows']):
        raise HTTPException(404, "Out of bounds")
    tid = int(state.terrain[y, x])
    tt = state.terrain_types.get(tid, {})
    return {'x': x, 'y': y, 'terrain_id': tid, 'name': tt.get('name'), 'color': tt.get('color')}


@app.get("/api/observe/{x}/{y}")
def observe(x: int, y: int, radius: int = None):
    result = state.observe(x, y, radius)
    if 'error' in result:
        raise HTTPException(404, result['error'])
    return result


@app.get("/api/terrain_batch")
def terrain_batch(min_x: int, min_y: int, max_x: int, max_y: int):
    cfg = state.get_config()
    min_x, min_y = max(0, min_x), max(0, min_y)
    max_x, max_y = min(cfg['grid_cols'], max_x), min(cfg['grid_rows'], max_y)
    cells = [[int(state.terrain[y, x]) for x in range(min_x, max_x)] for y in range(min_y, max_y)]
    return {'min_x': min_x, 'min_y': min_y, 'cells': cells}


@app.get("/api/god_mode/corridors")
def get_corridors():
    return state.get_corridors()


@app.get("/api/god_mode/signs")
def get_signs():
    return state.get_all_signs()


@app.post("/api/time")
def set_time(update: TimeUpdate):
    state.set_time(update.time_of_day)
    return {'time_of_day': state.time_of_day}


@app.get("/api/species")
def get_species():
    return state.species


@app.post("/api/regenerate")
def regenerate(seed: int = None):
    state.generate(seed or 42)
    return {'status': 'regenerated'}


# Static files
os.makedirs("static", exist_ok=True)
os.makedirs("assets/species", exist_ok=True)


@app.get("/")
def root():
    return FileResponse("static/index.html")


app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
