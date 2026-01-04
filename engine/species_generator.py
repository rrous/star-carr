"""
Species Generator - Parses species_init.yaml → species placement, effects, signs
"""

import numpy as np
from typing import Dict, List, Tuple, Any


class SpeciesGenerator:
    def __init__(self, rules: dict, terrain_ids: dict):
        self.rules = rules
        self.terrain_ids = terrain_ids
        self.species = rules.get('species', {})
        self.tags = rules.get('tags', {})
        self.symbols = rules.get('symbols', {})
        self.state_defs = rules.get('state_definitions', {})
    
    def generate(
        self,
        terrain: np.ndarray,
        corridors: Dict[str, np.ndarray],
        seed: int = None
    ) -> Dict[str, Any]:
        """Generate all species data."""
        if seed is not None:
            np.random.seed(seed)
        
        rows, cols = terrain.shape
        
        # Roll predator presence
        predator_presence = self._roll_predators()
        
        # Place species (predators first)
        locations = {}
        for category in [['predator'], ['large_herbivore', 'medium_herbivore'], ['aquatic'], ['tree', 'shrub', 'plant']]:
            for sp_id, sp_data in self.species.items():
                if sp_data.get('category') not in category:
                    continue
                if not predator_presence.get(sp_id, True):
                    locations[sp_id] = []
                    continue
                locations[sp_id] = self._place_species(sp_id, sp_data, terrain, corridors)
        
        # Process effects (exclusion zones, damage)
        modifiers = self._process_effects(locations, terrain)
        
        # Apply modifiers
        locations = self._apply_modifiers(locations, modifiers)
        
        # Generate presence arrays
        presence = {}
        for sp_id, locs in locations.items():
            arr = np.zeros((rows, cols), dtype=np.uint8)
            for x, y in locs:
                if 0 <= y < rows and 0 <= x < cols:
                    arr[y, x] = 1
            
            # Apply damage states
            if sp_id in modifiers.get('states', {}):
                arr = self._apply_states(arr, modifiers['states'][sp_id])
            
            presence[sp_id] = arr
        
        # Generate signs
        signs = self._generate_signs(locations, terrain)
        
        return {
            'presence': presence,
            'locations': locations,
            'predator_presence': predator_presence,
            'signs': signs,
        }
    
    def _roll_predators(self) -> dict:
        presence = {}
        for sp_id, sp_data in self.species.items():
            prob = sp_data.get('distribution', {}).get('presence_probability')
            if prob is not None:
                presence[sp_id] = np.random.random() < prob
                print(f"  {sp_id}: {'PRESENT' if presence[sp_id] else 'absent'}")
            else:
                presence[sp_id] = True
        
        # Human always present
        presence['_human_presence'] = True
        return presence
    
    def _place_species(
        self,
        sp_id: str,
        sp_data: dict,
        terrain: np.ndarray,
        corridors: Dict[str, np.ndarray]
    ) -> List[Tuple[int, int]]:
        dist = sp_data.get('distribution', {})
        if not dist:
            return []
        
        rows, cols = terrain.shape
        
        # Build probability map
        prob = np.zeros((rows, cols), dtype=np.float32)
        
        for tname, weight in dist.get('terrain_weights', {}).items():
            tid = self.terrain_ids.get(tname, -1)
            if tid >= 0:
                prob[terrain == tid] = weight
        
        # Corridor bonuses
        for cname, bonus in dist.get('corridor_bonus', {}).items():
            mask = corridors.get(cname)
            if mask is not None:
                prob[mask] *= bonus
        
        # Max water distance
        max_wd = dist.get('max_water_distance')
        if max_wd is not None:
            water_ids = [self.terrain_ids.get('deep_water', 0), self.terrain_ids.get('shallow_water', 1)]
            water = np.isin(terrain, water_ids)
            from scipy.ndimage import distance_transform_edt
            wd = distance_transform_edt(~water)
            prob[wd > max_wd] = 0
        
        category = sp_data.get('category', '')
        if category in ['tree', 'shrub', 'plant']:
            return self._place_vegetation(dist, prob, rows, cols)
        else:
            return self._place_animal(dist, prob, rows, cols)
    
    def _place_vegetation(self, dist: dict, prob: np.ndarray, rows: int, cols: int) -> List[Tuple]:
        locs = []
        clustering = dist.get('clustering', {})
        ctype = clustering.get('type', 'random')
        base = dist.get('base_density', 0.3)
        
        if ctype == 'stand':
            sr = clustering.get('stand_radius', [5, 15])
            tps = clustering.get('trees_per_stand', [15, 100])
            
            valid = np.argwhere(prob > 0)
            if len(valid) == 0:
                return locs
            
            area = np.pi * ((sr[0] + sr[1]) / 2) ** 2
            num_stands = max(1, int(len(valid) * base / area))
            
            indices = np.random.choice(len(valid), min(num_stands, len(valid)), replace=False)
            
            for idx in indices:
                cy, cx = valid[idx]
                r = np.random.randint(sr[0], sr[1] + 1)
                n = np.random.randint(tps[0], tps[1] + 1)
                
                for _ in range(n):
                    angle = np.random.uniform(0, 2 * np.pi)
                    d = np.random.uniform(0, r)
                    tx = int(cx + d * np.cos(angle))
                    ty = int(cy + d * np.sin(angle))
                    if 0 <= ty < rows and 0 <= tx < cols and prob[ty, tx] > 0:
                        locs.append((tx, ty))
        
        elif ctype == 'clump':
            spc = clustering.get('stems_per_clump', [3, 8])
            valid = np.argwhere(prob > 0)
            if len(valid) == 0:
                return locs
            
            num = max(1, int(len(valid) * base / 10))
            indices = np.random.choice(len(valid), min(num, len(valid)), replace=False)
            
            for idx in indices:
                cy, cx = valid[idx]
                n = np.random.randint(spc[0], spc[1] + 1)
                for _ in range(n):
                    tx = cx + np.random.randint(-1, 2)
                    ty = cy + np.random.randint(-1, 2)
                    if 0 <= ty < rows and 0 <= tx < cols and prob[ty, tx] > 0:
                        locs.append((tx, ty))
        
        elif ctype == 'continuous':
            for y in range(rows):
                for x in range(cols):
                    if prob[y, x] > 0 and np.random.random() < prob[y, x] * base * 3:
                        locs.append((x, y))
        
        else:
            for y in range(rows):
                for x in range(cols):
                    if prob[y, x] > 0 and np.random.random() < prob[y, x] * base:
                        locs.append((x, y))
        
        return locs
    
    def _place_animal(self, dist: dict, prob: np.ndarray, rows: int, cols: int) -> List[Tuple]:
        locs = []
        density = dist.get('density_per_km2', 5)
        gs = dist.get('group_size', [1, 5])
        spread = dist.get('group_spread', 3)
        
        total = int(density * 5)  # 5 km² map
        avg_group = (gs[0] + gs[1]) / 2
        num_groups = max(1, int(total / avg_group))
        
        valid = np.argwhere(prob > 0)
        if len(valid) == 0:
            return locs
        
        weights = np.array([prob[y, x] for y, x in valid])
        weights /= weights.sum()
        
        for _ in range(num_groups):
            idx = np.random.choice(len(valid), p=weights)
            cy, cx = valid[idx]
            size = np.random.randint(gs[0], gs[1] + 1)
            
            for _ in range(size):
                ox = np.random.randint(-spread, spread + 1)
                oy = np.random.randint(-spread, spread + 1)
                ax, ay = cx + ox, cy + oy
                if 0 <= ay < rows and 0 <= ax < cols and prob[ay, ax] > 0:
                    locs.append((ax, ay))
        
        return locs
    
    def _process_effects(self, locations: Dict, terrain: np.ndarray) -> Dict:
        rows, cols = terrain.shape
        modifiers = {'probability': {}, 'states': {}}
        
        # Process human presence
        hp = self.rules.get('_human_presence', {})
        if hp:
            platform_id = self.terrain_ids.get('platform', 8)
            platform_locs = [(x, y) for y, x in np.argwhere(terrain == platform_id)]
            
            for eff in hp.get('effects', []):
                self._apply_effect(eff, platform_locs, terrain, modifiers, rows, cols)
        
        # Process species effects
        for sp_id, locs in locations.items():
            if not locs:
                continue
            sp_data = self.species.get(sp_id, {})
            for eff in sp_data.get('effects', []):
                self._apply_effect(eff, locs, terrain, modifiers, rows, cols)
        
        return modifiers
    
    def _apply_effect(self, eff: dict, locs: List, terrain: np.ndarray, modifiers: Dict, rows: int, cols: int):
        etype = eff.get('effect')
        params = eff.get('params', {})
        
        if etype == 'excludes':
            targets = self._get_targets(eff.get('targets', {}))
            radius = params.get('radius', 10)
            prob = params.get('probability', 0.5)
            
            influence = self._compute_influence(locs, radius, rows, cols)
            
            for t in targets:
                if t not in modifiers['probability']:
                    modifiers['probability'][t] = np.ones((rows, cols), dtype=np.float32)
                modifiers['probability'][t] *= (1.0 - prob * influence)
        
        elif etype == 'damages':
            targets = self._get_targets(eff.get('targets', {}))
            radius = params.get('radius', 5)
            prob = params.get('probability', 0.5)
            state_def = params.get('state_definition')
            
            influence = self._compute_influence(locs, radius, rows, cols) * prob
            
            for t in targets:
                if t not in modifiers['states']:
                    modifiers['states'][t] = {'influence': np.zeros((rows, cols)), 'def': state_def}
                modifiers['states'][t]['influence'] = np.maximum(modifiers['states'][t]['influence'], influence)
    
    def _get_targets(self, spec: dict) -> List[str]:
        targets = []
        
        if 'tag' in spec:
            targets.extend(self.tags.get(spec['tag'], []))
        
        if 'category' in spec:
            cats = spec['category'] if isinstance(spec['category'], list) else [spec['category']]
            for sp_id, sp_data in self.species.items():
                if sp_data.get('category') in cats:
                    targets.append(sp_id)
        
        return targets
    
    def _compute_influence(self, locs: List, radius: int, rows: int, cols: int) -> np.ndarray:
        field = np.zeros((rows, cols), dtype=np.float32)
        
        for x, y in locs:
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < rows and 0 <= nx < cols:
                        dist = np.sqrt(dx*dx + dy*dy)
                        if dist <= radius:
                            inf = max(0, 1 - dist / radius)
                            field[ny, nx] = max(field[ny, nx], inf)
        
        return field
    
    def _apply_modifiers(self, locations: Dict, modifiers: Dict) -> Dict:
        new_locs = {}
        
        for sp_id, locs in locations.items():
            if sp_id not in modifiers['probability'] or not locs:
                new_locs[sp_id] = locs
                continue
            
            mod = modifiers['probability'][sp_id]
            filtered = []
            for x, y in locs:
                if 0 <= y < mod.shape[0] and 0 <= x < mod.shape[1]:
                    if np.random.random() < mod[y, x]:
                        filtered.append((x, y))
                else:
                    filtered.append((x, y))
            new_locs[sp_id] = filtered
        
        return new_locs
    
    def _apply_states(self, presence: np.ndarray, state_info: dict) -> np.ndarray:
        influence = state_info['influence']
        state_def = self.state_defs.get(state_info['def'], {})
        transitions = state_def.get('transitions', {})
        
        if not transitions:
            return presence
        
        result = presence.copy()
        indices = np.argwhere(presence > 0)
        
        for y, x in indices:
            inf = influence[y, x]
            
            for level in transitions.values():
                if inf <= level.get('threshold', 1.0):
                    probs = level.get('probs', {})
                    roll = np.random.random()
                    cum = 0
                    for state, p in probs.items():
                        cum += p
                        if roll < cum:
                            result[y, x] = int(state)
                            break
                    break
        
        return result
    
    def _generate_signs(self, locations: Dict, terrain: np.ndarray) -> List[dict]:
        signs = []
        rows, cols = terrain.shape
        
        for sp_id, locs in locations.items():
            if not locs:
                continue
            
            sp_data = self.species.get(sp_id, {})
            for eff in sp_data.get('effects', []):
                if eff.get('effect') != 'creates_sign':
                    continue
                
                sign_type = eff.get('sign')
                params = eff.get('params', {})
                radius = params.get('radius', 2)
                prob = params.get('probability', 0.3)
                tfilter = params.get('terrain_filter')
                
                tids = [self.terrain_ids.get(t, -1) for t in tfilter] if tfilter else None
                
                for x, y in locs:
                    for dy in range(-radius, radius + 1):
                        for dx in range(-radius, radius + 1):
                            if dx*dx + dy*dy > radius*radius:
                                continue
                            ny, nx = y + dy, x + dx
                            if not (0 <= ny < rows and 0 <= nx < cols):
                                continue
                            if tids and terrain[ny, nx] not in tids:
                                continue
                            
                            dist = np.sqrt(dx*dx + dy*dy)
                            local_p = prob * (1 - dist / (radius + 1))
                            if np.random.random() < local_p:
                                signs.append({'type': sign_type, 'x': int(nx), 'y': int(ny)})
        
        # Dedupe
        seen = set()
        unique = []
        for s in signs:
            key = (s['type'], s['x'], s['y'])
            if key not in seen:
                seen.add(key)
                unique.append(s)
        
        return unique
