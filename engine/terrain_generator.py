"""
Terrain Generator - Parses terrain_init.yaml → numpy arrays + corridors
"""

import numpy as np
from scipy.ndimage import distance_transform_edt, binary_dilation
import heapq
from typing import Dict, Tuple, List


class TerrainGenerator:
    def __init__(self, rules: dict):
        self.rules = rules
        self.grid = rules['grid']
        self.cols = self.grid['cols']
        self.rows = self.grid['rows']
        
        # Build terrain name→id lookup
        self.terrain_ids = {v['name']: int(k) for k, v in rules['terrain_types'].items()}
        self.terrain_types = {int(k): v for k, v in rules['terrain_types'].items()}
    
    def generate(self, seed: int = None) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Generate terrain array and corridor masks."""
        if seed is not None:
            np.random.seed(seed)
        
        terrain = self._generate_terrain()
        corridors = self._generate_corridors(terrain)
        
        return terrain, corridors
    
    def _generate_terrain(self) -> np.ndarray:
        terrain = np.zeros((self.rows, self.cols), dtype=np.uint8)
        lake = self.rules['lake']
        
        cx, cy = lake['center_x'], lake['center_y']
        rx, ry = lake['radius_x'], lake['radius_y']
        noise_min, noise_max = lake['noise_range']
        
        for y in range(self.rows):
            for x in range(self.cols):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                dist = np.sqrt(dx*dx + dy*dy) + np.random.uniform(noise_min, noise_max)
                
                # Find zone
                assigned = False
                for zone in lake['zones']:
                    if dist < zone['max_dist']:
                        t = zone['terrain']
                        if isinstance(t, list):
                            weights = zone.get('weights', [1/len(t)]*len(t))
                            t = np.random.choice(t, p=weights)
                        terrain[y, x] = self.terrain_ids[t]
                        assigned = True
                        break
                
                if not assigned:
                    default = self.rules['default_terrain']
                    t = np.random.choice(default['options'], p=default['weights'])
                    terrain[y, x] = self.terrain_ids[t]
        
        # Platform
        spawn = self.rules['spawn']
        platform_id = self.terrain_ids['platform']
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                py, px = spawn['y'] + dy, spawn['x'] + dx
                if 0 <= py < self.rows and 0 <= px < self.cols:
                    terrain[py, px] = platform_id
        
        # Grassland patches
        patches = self.rules.get('grassland_patches', {})
        grass_id = self.terrain_ids['grassland']
        water_ids = [self.terrain_ids['deep_water'], self.terrain_ids['shallow_water']]
        
        for _ in range(patches.get('count', 0)):
            region = patches['region']
            pcx = np.random.randint(region['x'][0], region['x'][1])
            pcy = np.random.randint(region['y'][0], region['y'][1])
            r = np.random.randint(patches['radius'][0], patches['radius'][1])
            
            for y in range(max(0, pcy-r), min(self.rows, pcy+r)):
                for x in range(max(0, pcx-r), min(self.cols, pcx+r)):
                    if (x-pcx)**2 + (y-pcy)**2 < r*r:
                        if terrain[y, x] not in water_ids + [platform_id]:
                            terrain[y, x] = grass_id
        
        return terrain
    
    def _generate_corridors(self, terrain: np.ndarray) -> Dict[str, np.ndarray]:
        corridors = {}
        corridor_rules = self.rules.get('corridors', {})
        
        if 'water_edge' in corridor_rules:
            corridors['water_edge'] = self._gen_water_edge(terrain, corridor_rules['water_edge'])
        
        if 'ecotone' in corridor_rules:
            corridors['ecotone'] = self._gen_ecotone(terrain, corridor_rules['ecotone'])
        
        if 'game_trail' in corridor_rules:
            corridors['game_trail'] = self._gen_game_trails(terrain, corridor_rules['game_trail'])
        
        return corridors
    
    def _gen_water_edge(self, terrain: np.ndarray, cfg: dict) -> np.ndarray:
        width = cfg.get('width', 3)
        water_ids = [self.terrain_ids[t] for t in cfg.get('source_terrain', ['deep_water', 'shallow_water'])]
        water_mask = np.isin(terrain, water_ids)
        
        if not water_mask.any():
            return np.zeros_like(terrain, dtype=bool)
        
        dist = distance_transform_edt(~water_mask)
        return (dist > 0) & (dist <= width)
    
    def _gen_ecotone(self, terrain: np.ndarray, cfg: dict) -> np.ndarray:
        width = cfg.get('width', 2)
        ecotone = np.zeros((self.rows, self.cols), dtype=bool)
        
        for y in range(self.rows):
            for x in range(self.cols):
                center = terrain[y, x]
                for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < self.rows and 0 <= nx < self.cols:
                        if terrain[ny, nx] != center:
                            ecotone[y, x] = True
                            break
        
        if width > 1:
            struct = np.ones((width*2+1, width*2+1), dtype=bool)
            ecotone = binary_dilation(ecotone, structure=struct)
        
        return ecotone
    
    def _gen_game_trails(self, terrain: np.ndarray, cfg: dict) -> np.ndarray:
        trail_mask = np.zeros((self.rows, self.cols), dtype=bool)
        
        from_ids = [self.terrain_ids[t] for t in cfg['endpoints']['from']]
        to_ids = [self.terrain_ids[t] for t in cfg['endpoints']['to']]
        
        from_mask = np.isin(terrain, from_ids)
        to_mask = np.isin(terrain, to_ids)
        
        if not from_mask.any() or not to_mask.any():
            return trail_mask
        
        from_pts = np.argwhere(from_mask)
        to_pts = np.argwhere(to_mask)
        
        cost_map = self._build_cost_map(terrain)
        count = cfg.get('count', 5)
        
        if len(from_pts) > count * 2:
            indices = np.random.choice(len(from_pts), count * 2, replace=False)
            from_pts = from_pts[indices]
        
        trails = 0
        for start in from_pts:
            if trails >= count:
                break
            
            dists = [np.sqrt((start[0]-ep[0])**2 + (start[1]-ep[1])**2) for ep in to_pts]
            end = to_pts[np.argmin(dists)]
            
            path = self._astar(tuple(start), tuple(end), cost_map)
            if path:
                for y, x in path:
                    trail_mask[y, x] = True
                trails += 1
        
        return trail_mask
    
    def _build_cost_map(self, terrain: np.ndarray) -> np.ndarray:
        cost = np.ones_like(terrain, dtype=np.float32)
        
        costs = {
            'deep_water': 100, 'shallow_water': 5, 'reed_bed': 2, 'wetland': 3,
            'carr_woodland': 1, 'birch_woodland': 1, 'mixed_woodland': 1,
            'grassland': 2, 'platform': 50
        }
        
        for name, c in costs.items():
            if name in self.terrain_ids:
                cost[terrain == self.terrain_ids[name]] = c
        
        return cost
    
    def _astar(self, start: Tuple, end: Tuple, cost_map: np.ndarray) -> List[Tuple]:
        def h(a, b):
            return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        
        open_set = [(h(start, end), 0, start)]
        came_from = {}
        g_score = {start: 0}
        counter = 0
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            if current == end:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                ny, nx = current[0] + dy, current[1] + dx
                if not (0 <= ny < self.rows and 0 <= nx < self.cols):
                    continue
                
                neighbor = (ny, nx)
                move_cost = 1.414 if (dy != 0 and dx != 0) else 1.0
                tentative_g = g_score[current] + cost_map[ny, nx] * move_cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    counter += 1
                    heapq.heappush(open_set, (tentative_g + h(neighbor, end), counter, neighbor))
        
        return []
