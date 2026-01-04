"""
State Manager - Handles world state loading/saving, observation context, conditions
With Upstash Redis persistence
"""

import numpy as np
import json
import os
import re
import base64
from typing import Dict, Any, Optional, List

# Redis client (optional - falls back to local files)
redis_client = None
try:
    import redis
    redis_url = os.environ.get('UPSTASH_REDIS_URL') or os.environ.get('REDIS_URL')
    if redis_url:
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print(f"Redis connected: {redis_url[:30]}...")
except Exception as e:
    print(f"Redis not available: {e}, using local files")


def np_to_b64(arr: np.ndarray) -> str:
    """Encode numpy array to base64 string."""
    return base64.b64encode(arr.tobytes()).decode('utf-8')


def b64_to_np(s: str, dtype, shape) -> np.ndarray:
    """Decode base64 string to numpy array."""
    return np.frombuffer(base64.b64decode(s), dtype=dtype).reshape(shape)


class StateManager:
    REDIS_KEY = 'star_carr:world'
    
    def __init__(self, rules: dict, data_dir: str = 'data'):
        self.rules = rules
        self.data_dir = data_dir
        self.redis = redis_client
        self.terrain_rules = rules.get('terrain', {})
        self.species_rules = rules.get('species', {})
        
        # Runtime state
        self.terrain = None
        self.corridors = {}
        self.species_presence = {}
        self.signs = []
        self.predator_presence = {}
        self.time_of_day = 'midday'
        self.season = 'spring'
        
        # Build lookups
        self.terrain_types = {int(k): v for k, v in self.terrain_rules.get('terrain_types', {}).items()}
        self.terrain_ids = {v['name']: int(k) for k, v in self.terrain_types.items()}
        self.symbols = self.species_rules.get('symbols', {})
        self.species = self.species_rules.get('species', {})
    
    def load_or_generate(self, seed: int = 42):
        """Load from Redis, then local files, or generate new world."""
        if self.redis and self._load_from_redis():
            return
        if os.path.exists(f'{self.data_dir}/terrain.npy'):
            self.load()
            # Sync to Redis if available
            if self.redis:
                self._save_to_redis()
        else:
            self.generate(seed)
    
    def generate(self, seed: int = 42):
        """Generate new world."""
        from .terrain_generator import TerrainGenerator
        from .species_generator import SpeciesGenerator
        
        print("Generating world...")
        
        tgen = TerrainGenerator(self.terrain_rules)
        self.terrain, self.corridors = tgen.generate(seed)
        
        sgen = SpeciesGenerator(self.species_rules, tgen.terrain_ids)
        result = sgen.generate(self.terrain, self.corridors, seed)
        
        self.species_presence = result['presence']
        self.signs = result['signs']
        self.predator_presence = result['predator_presence']
        
        print(f"Generated {len(self.signs)} signs")
        self.save()
        
        # Also save to Redis
        if self.redis:
            self._save_to_redis()
    
    def save(self):
        """Save state to files."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        np.save(f'{self.data_dir}/terrain.npy', self.terrain)
        
        # Corridors as bitfield
        bits = np.zeros_like(self.terrain, dtype=np.uint8)
        for i, name in enumerate(['water_edge', 'ecotone', 'game_trail']):
            if name in self.corridors:
                bits |= (self.corridors[name].astype(np.uint8) << i)
        np.save(f'{self.data_dir}/corridors.npy', bits)
        
        # Species
        for sp_id, arr in self.species_presence.items():
            np.save(f'{self.data_dir}/species_{sp_id}.npy', arr)
        
        with open(f'{self.data_dir}/signs.json', 'w') as f:
            json.dump(self.signs, f)
        
        with open(f'{self.data_dir}/predators.json', 'w') as f:
            json.dump(self.predator_presence, f)
    
    def load(self):
        """Load state from files."""
        print("Loading existing world...")
        
        self.terrain = np.load(f'{self.data_dir}/terrain.npy')
        
        if os.path.exists(f'{self.data_dir}/corridors.npy'):
            bits = np.load(f'{self.data_dir}/corridors.npy')
            for i, name in enumerate(['water_edge', 'ecotone', 'game_trail']):
                self.corridors[name] = (bits & (1 << i)) > 0
        
        for f in os.listdir(self.data_dir):
            if f.startswith('species_') and f.endswith('.npy'):
                sp_id = f[8:-4]
                self.species_presence[sp_id] = np.load(f'{self.data_dir}/{f}')
        
        if os.path.exists(f'{self.data_dir}/signs.json'):
            with open(f'{self.data_dir}/signs.json') as f:
                self.signs = json.load(f)
        
        if os.path.exists(f'{self.data_dir}/predators.json'):
            with open(f'{self.data_dir}/predators.json') as f:
                self.predator_presence = json.load(f)
        
        print(f"Loaded: {self.terrain.shape}, {len(self.signs)} signs")
    
    def _save_to_redis(self):
        """Save full world state to Redis."""
        try:
            rows, cols = self.terrain.shape
            
            data = {
                'shape': [rows, cols],
                'terrain': np_to_b64(self.terrain),
                'corridors': {},
                'species': {},
                'signs': self.signs,
                'predator_presence': self.predator_presence,
                'time_of_day': self.time_of_day,
                'season': self.season,
            }
            
            # Corridors
            for name, mask in self.corridors.items():
                if mask is not None:
                    data['corridors'][name] = np_to_b64(mask.astype(np.uint8))
            
            # Species
            for sp_id, arr in self.species_presence.items():
                if arr is not None:
                    data['species'][sp_id] = np_to_b64(arr)
            
            self.redis.set(self.REDIS_KEY, json.dumps(data))
            print(f"Saved to Redis ({len(json.dumps(data)) // 1024} KB)")
            return True
        except Exception as e:
            print(f"Redis save failed: {e}")
            return False
    
    def _load_from_redis(self) -> bool:
        """Load full world state from Redis."""
        try:
            raw = self.redis.get(self.REDIS_KEY)
            if not raw:
                print("No data in Redis")
                return False
            
            data = json.loads(raw)
            rows, cols = data['shape']
            
            self.terrain = b64_to_np(data['terrain'], np.uint8, (rows, cols))
            
            self.corridors = {}
            for name, b64 in data.get('corridors', {}).items():
                self.corridors[name] = b64_to_np(b64, np.uint8, (rows, cols)).astype(bool)
            
            self.species_presence = {}
            for sp_id, b64 in data.get('species', {}).items():
                self.species_presence[sp_id] = b64_to_np(b64, np.uint8, (rows, cols))
            
            self.signs = data.get('signs', [])
            self.predator_presence = data.get('predator_presence', {})
            self.time_of_day = data.get('time_of_day', 'midday')
            self.season = data.get('season', 'spring')
            
            print(f"Loaded from Redis: {rows}x{cols}, {len(self.signs)} signs")
            
            # Also save locally as cache
            self.save()
            return True
        except Exception as e:
            print(f"Redis load failed: {e}")
            return False
    
    def get_config(self) -> dict:
        """Return config for frontend."""
        grid = self.terrain_rules.get('grid', {})
        spawn = self.terrain_rules.get('spawn', {})
        
        return {
            'grid_cols': grid.get('cols', 200),
            'grid_rows': grid.get('rows', 250),
            'spawn_x': spawn.get('x', 20),
            'spawn_y': spawn.get('y', 42),
            'visibility_radius': self.terrain_rules.get('visibility_radius', 3),
            'terrain_types': {str(k): {'name': v['name'], 'color': v['color']} for k, v in self.terrain_types.items()},
            'predator_presence': self.predator_presence,
            'time_of_day': self.time_of_day,
            'season': self.season,
            'symbols': self.symbols,
        }
    
    def observe(self, x: int, y: int, radius: int = None) -> dict:
        """Get observations at location."""
        cfg = self.get_config()
        radius = radius or cfg['visibility_radius']
        rows, cols = self.terrain.shape
        
        if not (0 <= x < cols and 0 <= y < rows):
            return {'error': 'Out of bounds'}
        
        context = self._build_context(x, y, radius)
        
        # Current terrain
        tid = int(self.terrain[y, x])
        
        # Visible terrains
        visible_terrains = []
        seen = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy > radius*radius:
                    continue
                cy, cx = y + dy, x + dx
                if 0 <= cy < rows and 0 <= cx < cols:
                    t = int(self.terrain[cy, cx])
                    if t not in seen:
                        seen.add(t)
                        tt = self.terrain_types.get(t, {})
                        visible_terrains.append({'id': t, 'name': tt.get('name', '?'), 'color': tt.get('color', '#888')})
        
        # Species observations
        observations = []
        for sp_id, presence in self.species_presence.items():
            cells, max_state = [], 0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx*dx + dy*dy > radius*radius:
                        continue
                    cy, cx = y + dy, x + dx
                    if 0 <= cy < rows and 0 <= cx < cols and presence[cy, cx] > 0:
                        cells.append((cx, cy))
                        max_state = max(max_state, int(presence[cy, cx]))
            
            if not cells:
                continue
            
            sp = self.species.get(sp_id, {})
            obs = sp.get('observation', {})
            
            # Build observation text with conditionals
            text = {f: obs.get(f, '') for f in ['visual', 'tactile', 'smell', 'sound', 'habitat', 'season_note', 'uses']}
            
            self_ctx = {'state': max_state}
            for ct in obs.get('conditional_texts', []):
                cond = ct.get('condition', '')
                ct_radius = ct.get('radius', radius)
                eval_ctx = context if ct_radius == radius else self._build_context(x, y, ct_radius)
                
                if self._eval_condition(cond, eval_ctx, self_ctx):
                    field = ct.get('append_to', '')
                    if field in text:
                        text[field] += ' ' + ct.get('text', '')
            
            observations.append({
                'species_id': sp_id,
                'common_name': sp.get('common', sp_id),
                'latin_name': sp.get('latin', ''),
                'category': sp.get('category', ''),
                'count': len(cells),
                'locations': cells,
                'state': max_state,
                'photo_url': f'/assets/species/{sp.get("photo")}' if sp.get('photo') else None,
                **text,
            })
        
        # Sort
        order = ['tree', 'shrub', 'plant', 'large_herbivore', 'medium_herbivore', 'predator', 'aquatic']
        observations.sort(key=lambda o: (order.index(o['category']) if o['category'] in order else 99, o['common_name']))
        
        # Signs
        visible_signs = []
        for s in self.signs:
            if (s['x'] - x)**2 + (s['y'] - y)**2 <= radius*radius:
                sym = self.symbols.get(s['type'], {})
                visible_signs.append({
                    'type': s['type'], 'x': s['x'], 'y': s['y'],
                    'char': sym.get('char', '?'), 'color': sym.get('color', '#888'),
                    'description': sym.get('description', ''),
                })
        
        # Corridors
        corridors_here = [n for n, m in self.corridors.items() if m is not None and m[y, x]]
        
        tt = self.terrain_types.get(tid, {})
        return {
            'location': {'x': x, 'y': y},
            'current_terrain': {'id': tid, 'name': tt.get('name', '?'), 'color': tt.get('color', '#888')},
            'visible_terrains': visible_terrains,
            'observations': observations,
            'signs': visible_signs,
            'corridors': corridors_here,
            'time_of_day': self.time_of_day,
            'season': self.season,
        }
    
    def _build_context(self, x: int, y: int, radius: int) -> dict:
        """Build context for condition evaluation."""
        rows, cols = self.terrain.shape
        ctx = {'species': {}, 'sign': {}, 'terrain': {}, 'time': {}, 'corridor': {}}
        
        # Terrain
        tid = int(self.terrain[y, x])
        ctx['terrain']['current'] = self.terrain_types.get(tid, {}).get('name', 'unknown')
        
        nearby = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    cy, cx = y + dy, x + dx
                    if 0 <= cy < rows and 0 <= cx < cols:
                        nearby.add(int(self.terrain[cy, cx]))
        ctx['terrain']['is_ecotone'] = len(nearby) > 1
        
        # Time
        ctx['time']['of_day'] = self.time_of_day
        ctx['time']['season'] = self.season
        
        # Corridors
        for name, mask in self.corridors.items():
            ctx['corridor'][name] = {'in': bool(mask[y, x]) if mask is not None else False}
        
        # Species
        for sp_id, presence in self.species_presence.items():
            cells, max_state, min_dist = 0, 0, 999
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx*dx + dy*dy > radius*radius:
                        continue
                    cy, cx = y + dy, x + dx
                    if 0 <= cy < rows and 0 <= cx < cols and presence[cy, cx] > 0:
                        cells += 1
                        max_state = max(max_state, int(presence[cy, cx]))
                        min_dist = min(min_dist, int(np.sqrt(dx*dx + dy*dy)))
            
            ctx['species'][sp_id] = {
                'present': cells > 0,
                'count': cells,
                'state': max_state,
                'distance': min_dist if cells > 0 else 999,
            }
        
        # Signs
        for s in self.signs:
            if (s['x'] - x)**2 + (s['y'] - y)**2 <= radius*radius:
                t = s['type']
                if t not in ctx['sign']:
                    ctx['sign'][t] = {'present': False, 'count': 0}
                ctx['sign'][t]['present'] = True
                ctx['sign'][t]['count'] += 1
        
        return ctx
    
    def _eval_condition(self, cond: str, ctx: dict, self_ctx: dict) -> bool:
        """Evaluate condition string."""
        try:
            cond = cond.strip()
            if not cond:
                return False
            
            if ' and ' in cond:
                return all(self._eval_condition(p.strip(), ctx, self_ctx) for p in cond.split(' and '))
            if ' or ' in cond:
                return any(self._eval_condition(p.strip(), ctx, self_ctx) for p in cond.split(' or '))
            
            # in [...]
            m = re.match(r'(.+)\s+in\s+\[(.+)\]', cond)
            if m:
                val = self._get_val(m.group(1).strip(), ctx, self_ctx)
                items = [i.strip().strip('"\'') for i in m.group(2).split(',')]
                return val in items
            
            # Comparisons
            for op in ['>=', '<=', '==', '!=', '>', '<']:
                if op in cond:
                    left, right = cond.split(op, 1)
                    lval = self._get_val(left.strip(), ctx, self_ctx)
                    rval = self._parse_val(right.strip())
                    if lval is None:
                        lval = 0
                    ops = {'>=': lambda a,b: a>=b, '<=': lambda a,b: a<=b, '==': lambda a,b: a==b,
                           '!=': lambda a,b: a!=b, '>': lambda a,b: a>b, '<': lambda a,b: a<b}
                    return ops[op](lval, rval)
            
            # Boolean
            return bool(self._get_val(cond, ctx, self_ctx))
        except:
            return False
    
    def _get_val(self, path: str, ctx: dict, self_ctx: dict) -> Any:
        parts = path.split('.')
        if parts[0] == 'self':
            obj = self_ctx
            parts = parts[1:]
        else:
            obj = ctx
        
        for p in parts:
            if isinstance(obj, dict):
                obj = obj.get(p)
            else:
                return None
        return obj
    
    def _parse_val(self, s: str) -> Any:
        s = s.strip()
        if s.lower() == 'true':
            return True
        if s.lower() == 'false':
            return False
        try:
            return int(s)
        except:
            pass
        try:
            return float(s)
        except:
            pass
        return s.strip('"\'')
    
    def set_time(self, time_of_day: str):
        valid = ['dawn', 'morning', 'midday', 'afternoon', 'dusk', 'night']
        if time_of_day in valid:
            self.time_of_day = time_of_day
            # Persist to Redis
            if self.redis:
                try:
                    raw = self.redis.get(self.REDIS_KEY)
                    if raw:
                        data = json.loads(raw)
                        data['time_of_day'] = time_of_day
                        self.redis.set(self.REDIS_KEY, json.dumps(data))
                except:
                    pass
    
    def get_corridors(self) -> dict:
        """Return all corridors for god mode."""
        result = {}
        cfg = self.terrain_rules.get('corridors', {})
        for name, mask in self.corridors.items():
            if mask is None:
                continue
            cells = np.argwhere(mask)
            result[name] = {
                'cells': [[int(x), int(y)] for y, x in cells],
                'color': cfg.get(name, {}).get('color', '#888'),
                'count': len(cells),
            }
        return result
    
    def get_all_signs(self) -> list:
        """Return all signs for god mode."""
        by_type = {}
        for s in self.signs:
            t = s['type']
            if t not in by_type:
                sym = self.symbols.get(t, {})
                by_type[t] = {
                    'type': t, 'char': sym.get('char', '?'),
                    'color': sym.get('color', '#888'),
                    'description': sym.get('description', ''),
                    'locations': [],
                }
            by_type[t]['locations'].append({'x': s['x'], 'y': s['y']})
        return list(by_type.values())
