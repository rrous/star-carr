"""
State Manager - Handles world state persistence via Upstash Redis
"""

import os
import json
import base64
import httpx
import numpy as np
from typing import Optional
from datetime import datetime


class StateManager:
    """Manages world state in Upstash Redis."""
    
    def __init__(self):
        self.redis_url = os.environ.get('UPSTASH_REDIS_REST_URL')
        self.redis_token = os.environ.get('UPSTASH_REDIS_REST_TOKEN')
        self.enabled = bool(self.redis_url and self.redis_token)
        
        if self.enabled:
            self.headers = {
                'Authorization': f'Bearer {self.redis_token}',
                'Content-Type': 'application/json'
            }
            print(f"StateManager: Redis enabled at {self.redis_url}")
        else:
            print("StateManager: Redis not configured, using local state only")
    
    def _request(self, command: list) -> Optional[dict]:
        """Execute Redis command via REST API."""
        if not self.enabled:
            return None
        
        try:
            response = httpx.post(
                self.redis_url,
                headers=self.headers,
                json=command,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Redis error: {e}")
            return None
    
    def save_terrain(self, terrain: np.ndarray) -> bool:
        """Save terrain array to Redis."""
        if not self.enabled:
            return False
        
        # Encode numpy array as base64
        data = base64.b64encode(terrain.tobytes()).decode('utf-8')
        metadata = {
            'shape': terrain.shape,
            'dtype': str(terrain.dtype),
            'data': data,
            'updated': datetime.utcnow().isoformat()
        }
        
        result = self._request(['SET', 'terrain', json.dumps(metadata)])
        return result is not None and result.get('result') == 'OK'
    
    def load_terrain(self) -> Optional[np.ndarray]:
        """Load terrain array from Redis."""
        if not self.enabled:
            return None
        
        result = self._request(['GET', 'terrain'])
        if not result or not result.get('result'):
            return None
        
        try:
            metadata = json.loads(result['result'])
            data = base64.b64decode(metadata['data'])
            shape = tuple(metadata['shape'])
            dtype = np.dtype(metadata['dtype'])
            return np.frombuffer(data, dtype=dtype).reshape(shape)
        except Exception as e:
            print(f"Error loading terrain: {e}")
            return None
    
    def save_species(self, species: np.ndarray) -> bool:
        """Save species array to Redis."""
        if not self.enabled:
            return False
        
        data = base64.b64encode(species.tobytes()).decode('utf-8')
        metadata = {
            'shape': species.shape,
            'dtype': str(species.dtype),
            'data': data,
            'updated': datetime.utcnow().isoformat()
        }
        
        result = self._request(['SET', 'species', json.dumps(metadata)])
        return result is not None and result.get('result') == 'OK'
    
    def load_species(self) -> Optional[np.ndarray]:
        """Load species array from Redis."""
        if not self.enabled:
            return None
        
        result = self._request(['GET', 'species'])
        if not result or not result.get('result'):
            return None
        
        try:
            metadata = json.loads(result['result'])
            data = base64.b64decode(metadata['data'])
            shape = tuple(metadata['shape'])
            dtype = np.dtype(metadata['dtype'])
            return np.frombuffer(data, dtype=dtype).reshape(shape)
        except Exception as e:
            print(f"Error loading species: {e}")
            return None
    
    def save_game_state(self, state: dict) -> bool:
        """Save game state (month, season, etc.) to Redis."""
        if not self.enabled:
            return False
        
        state['updated'] = datetime.utcnow().isoformat()
        result = self._request(['SET', 'game_state', json.dumps(state)])
        return result is not None and result.get('result') == 'OK'
    
    def load_game_state(self) -> Optional[dict]:
        """Load game state from Redis."""
        if not self.enabled:
            return None
        
        result = self._request(['GET', 'game_state'])
        if not result or not result.get('result'):
            return None
        
        try:
            return json.loads(result['result'])
        except Exception as e:
            print(f"Error loading game state: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.enabled:
            return False
        
        result = self._request(['EXISTS', key])
        return result is not None and result.get('result', 0) > 0
    
    def has_world_state(self) -> bool:
        """Check if world state exists in Redis."""
        return self.exists('terrain') and self.exists('species')
    
    def clear_all(self) -> bool:
        """Clear all world state from Redis."""
        if not self.enabled:
            return False
        
        for key in ['terrain', 'species', 'game_state']:
            self._request(['DEL', key])
        return True


# Singleton instance
state_manager = StateManager()
