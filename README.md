# Star Carr v2 - Rule Engine + Upstash Redis

## New Architecture

```
star-carr/
├── main.py                 # FastAPI server
├── requirements.txt
├── render.yaml
│
├── engine/                 # Rule engine
│   ├── __init__.py
│   ├── terrain_generator.py    # YAML → terrain array
│   ├── species_generator.py    # YAML → species placement
│   └── state_manager.py        # Upstash Redis integration
│
├── rules/                  # Designer-editable YAML
│   ├── terrain_init.yaml       # Terrain zones & types
│   └── species_init.yaml       # Species definitions
│
├── static/                 # Frontend
│   ├── index.html
│   ├── app.js
│   └── style.css
│
└── assets/
    └── species/            # Species images
        └── placeholder.svg
```

## How It Works

1. **Startup**: Server loads YAML rules
2. **Redis check**: If world state exists in Redis → load it
3. **Generate**: If no Redis state → generate from rules → save to Redis
4. **Serve**: API serves terrain/species from memory
5. **Persist**: State survives restarts via Redis

## Setup Instructions

### 1. Upstash Redis (already done)

Your credentials:
```
UPSTASH_REDIS_REST_URL=https://proven-flamingo-13647.upstash.io
UPSTASH_REDIS_REST_TOKEN=ATVPAAIncDI2Y2Y2MDE4MjczOGQ0N2FhOTVlNjExMzQ2MGUzZWM3OXAyMTM2NDc
```

### 2. Update GitHub Repository

Replace all files in your `star-carr` repo with the new structure:

**Delete old files:**
- `config.py`
- `generate_data.py`

**Add new files:**
- `engine/` folder (all 4 files)
- `rules/` folder (2 YAML files)
- `assets/species/placeholder.svg`
- Updated `main.py`
- Updated `requirements.txt`
- Updated `render.yaml`

### 3. Add Environment Variables in Render

1. Go to https://dashboard.render.com
2. Select `star-carr` service
3. Click **Environment** tab
4. Add two variables:

| Key | Value |
|-----|-------|
| `UPSTASH_REDIS_REST_URL` | `https://proven-flamingo-13647.upstash.io` |
| `UPSTASH_REDIS_REST_TOKEN` | `ATVPAAIncDI2Y2Y2MDE4MjczOGQ0N2FhOTVlNjExMzQ2MGUzZWM3OXAyMTM2NDc` |

5. Click **Save Changes**

### 4. Deploy

Push to GitHub → Render auto-deploys

Or click **Manual Deploy** in Render dashboard

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/config` | Grid config, terrain types |
| `GET /api/observe/{x}/{y}` | Species in visibility radius |
| `GET /api/terrain/{x}/{y}` | Single cell terrain |
| `GET /api/terrain_batch` | Terrain for map rendering |
| `GET /api/species` | Full species database |
| `GET /api/game_state` | Current month/season |
| `POST /api/regenerate` | Force regenerate world |

## For Designers

### Edit Terrain (`rules/terrain_init.yaml`)

Add a new zone:
```yaml
zones:
  - name: my_new_clearing
    terrain: grassland
    shape: ellipse
    center: [100, 100]
    radius: [20, 15]
```

Shapes supported:
- `ellipse`: center + radius
- `rect`: bounds [x1, y1, x2, y2]
- `polygon`: points [[x,y], [x,y], ...]

### Edit Species (`rules/species_init.yaml`)

Add a new species:
```yaml
species:
  hedgehog:
    id: 50
    latin: Erinaceus europaeus
    category: medium_herbivore
    abundance: occasional
    terrains: [grassland, birch_woodland]
    photo: "/assets/species/hedgehog.jpg"
    observations:
      visual: "Small spiny mammal..."
      # ... other observations
```

### After Editing Rules

1. Push changes to GitHub
2. Render redeploys automatically
3. Call `POST /api/regenerate` to regenerate world from new rules

Or: Delete Redis keys to force regeneration on next restart

## Troubleshooting

### "Redis not configured"
- Check environment variables in Render dashboard
- Ensure no typos in variable names

### World not updating after rule changes
- Call `POST /api/regenerate` endpoint
- Or clear Redis manually via Upstash console

### Species not appearing
- Check terrain names in `species_init.yaml` match `terrain_init.yaml`
- Verify species abundance isn't `very_rare` (may need many cells to find one)

## Future Enhancements

- [ ] `seasons.yaml` for monthly changes
- [ ] Cron job to advance time (1 hour = 1 month)
- [ ] Admin UI for editing rules
- [ ] Multiple save slots
