/**
 * Star Carr Mesolithic Scholar Simulator - Game Engine
 * v2: Bigger cells, species symbols on map, hover observations
 */

// Game state
const state = {
    config: null,
    playerX: 0,
    playerY: 0,
    currentObservations: null,
    hoveredSpecies: null,
    visibleSpeciesLocations: []
};

// Canvas setup
const canvas = document.getElementById('map-canvas');
const ctx = canvas.getContext('2d');
const CELL_SIZE = 24;  // 3x bigger (was 8)
const VIEW_RADIUS = 15;

// Species symbols by category
const SPECIES_SYMBOLS = {
    tree: '🌳',
    shrub: '🌿',
    plant: '🌱',
    large_herbivore: '🦌',
    medium_herbivore: '🦫',
    predator: '🐺',
    aquatic: '🐟',
    bird: '🦅'
};

// DOM elements
const locationText = document.getElementById('location-text');
const terrainText = document.getElementById('terrain-text');
const terrainList = document.getElementById('terrain-list');
const observationsList = document.getElementById('observations-list');

/**
 * Initialize the game
 */
async function init() {
    try {
        const response = await fetch('/api/config');
        state.config = await response.json();
        
        state.playerX = state.config.spawn_x;
        state.playerY = state.config.spawn_y;
        
        setupControls();
        await updateView();
        
        console.log('Star Carr initialized', state.config);
    } catch (error) {
        console.error('Failed to initialize:', error);
        locationText.textContent = 'Error loading game. Check console.';
    }
}

/**
 * Setup keyboard and mouse controls
 */
function setupControls() {
    // Keyboard
    document.addEventListener('keydown', (e) => {
        let dx = 0, dy = 0;
        
        switch(e.key) {
            case 'ArrowUp': case 'w': case 'W': dy = -1; break;
            case 'ArrowDown': case 's': case 'S': dy = 1; break;
            case 'ArrowLeft': case 'a': case 'A': dx = -1; break;
            case 'ArrowRight': case 'd': case 'D': dx = 1; break;
            default: return;
        }
        
        e.preventDefault();
        movePlayer(dx, dy);
    });
    
    // Mouse click - move player
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        const dx = Math.round((clickX - centerX) / CELL_SIZE);
        const dy = Math.round((clickY - centerY) / CELL_SIZE);
        
        if (dx !== 0 || dy !== 0) {
            const stepX = dx === 0 ? 0 : (dx > 0 ? 1 : -1);
            const stepY = dy === 0 ? 0 : (dy > 0 ? 1 : -1);
            movePlayer(stepX, stepY);
        }
    });
    
    // Mouse hover - show species info
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        const dx = Math.round((mouseX - centerX) / CELL_SIZE);
        const dy = Math.round((mouseY - centerY) / CELL_SIZE);
        
        const worldX = state.playerX + dx;
        const worldY = state.playerY + dy;
        
        const hoveredLoc = state.visibleSpeciesLocations.find(
            loc => loc.x === worldX && loc.y === worldY
        );
        
        if (hoveredLoc) {
            if (state.hoveredSpecies !== hoveredLoc.species.id) {
                state.hoveredSpecies = hoveredLoc.species.id;
                renderObservations(state.currentObservations, hoveredLoc.species.id);
            }
        } else {
            if (state.hoveredSpecies !== null) {
                state.hoveredSpecies = null;
                renderObservations(state.currentObservations, null);
            }
        }
    });
    
    canvas.addEventListener('mouseleave', () => {
        state.hoveredSpecies = null;
        renderObservations(state.currentObservations, null);
    });
}

/**
 * Move player by delta
 */
async function movePlayer(dx, dy) {
    const newX = state.playerX + dx;
    const newY = state.playerY + dy;
    
    if (newX < 0 || newX >= state.config.grid_cols ||
        newY < 0 || newY >= state.config.grid_rows) {
        return;
    }
    
    state.playerX = newX;
    state.playerY = newY;
    
    await updateView();
}

/**
 * Fetch terrain batch for visible area
 */
async function fetchTerrainBatch(minX, minY, maxX, maxY) {
    const url = `/api/terrain_batch?min_x=${minX}&min_y=${minY}&max_x=${maxX}&max_y=${maxY}`;
    const response = await fetch(url);
    return await response.json();
}

/**
 * Fetch observations at current location
 */
async function fetchObservations() {
    const url = `/api/observe/${state.playerX}/${state.playerY}`;
    const response = await fetch(url);
    return await response.json();
}

/**
 * Update entire view (map + observations)
 */
async function updateView() {
    const minX = Math.max(0, state.playerX - VIEW_RADIUS);
    const minY = Math.max(0, state.playerY - VIEW_RADIUS);
    const maxX = Math.min(state.config.grid_cols, state.playerX + VIEW_RADIUS + 1);
    const maxY = Math.min(state.config.grid_rows, state.playerY + VIEW_RADIUS + 1);
    
    const [terrainData, observations] = await Promise.all([
        fetchTerrainBatch(minX, minY, maxX, maxY),
        fetchObservations()
    ]);
    
    state.currentObservations = observations;
    state.visibleSpeciesLocations = [];
    
    renderMap(terrainData, observations);
    renderLocationInfo(observations);
    renderObservations(observations, null);
}

/**
 * Render the map canvas with species symbols
 */
function renderMap(terrainData, observations) {
    const { min_x, min_y, cells } = terrainData;
    const visRadius = state.config.visibility_radius;
    
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const offsetX = canvas.width / 2 - (state.playerX - min_x) * CELL_SIZE - CELL_SIZE / 2;
    const offsetY = canvas.height / 2 - (state.playerY - min_y) * CELL_SIZE - CELL_SIZE / 2;
    
    state.visibleSpeciesLocations = [];
    
    // Draw terrain cells
    for (let row = 0; row < cells.length; row++) {
        for (let col = 0; col < cells[row].length; col++) {
            const worldX = min_x + col;
            const worldY = min_y + row;
            
            const dx = worldX - state.playerX;
            const dy = worldY - state.playerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            const screenX = offsetX + col * CELL_SIZE;
            const screenY = offsetY + row * CELL_SIZE;
            
            if (dist <= visRadius) {
                const terrainId = cells[row][col];
                const terrain = state.config.terrain_types[terrainId];
                ctx.fillStyle = terrain ? terrain.color : '#888';
            } else {
                ctx.fillStyle = '#2a2a3e';
            }
            
            ctx.fillRect(screenX, screenY, CELL_SIZE - 1, CELL_SIZE - 1);
        }
    }
    
    // Draw species symbols
    for (const sp of observations.observations) {
        if (sp.locations) {
            for (const loc of sp.locations) {
                const dx = loc.x - state.playerX;
                const dy = loc.y - state.playerY;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist <= visRadius) {
                    const screenX = offsetX + (loc.x - min_x) * CELL_SIZE;
                    const screenY = offsetY + (loc.y - min_y) * CELL_SIZE;
                    
                    const symbol = SPECIES_SYMBOLS[sp.category] || '?';
                    ctx.font = `${CELL_SIZE - 6}px serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(symbol, screenX + CELL_SIZE/2, screenY + CELL_SIZE/2);
                    
                    state.visibleSpeciesLocations.push({
                        x: loc.x,
                        y: loc.y,
                        species: sp
                    });
                }
            }
        }
    }
    
    // Draw player
    const playerScreenX = canvas.width / 2 - CELL_SIZE / 2;
    const playerScreenY = canvas.height / 2 - CELL_SIZE / 2;
    
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(playerScreenX + CELL_SIZE / 2, playerScreenY + CELL_SIZE / 2, CELL_SIZE / 3, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw visibility circle
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, visRadius * CELL_SIZE, 0, Math.PI * 2);
    ctx.stroke();
}

/**
 * Render location info under map
 */
function renderLocationInfo(data) {
    locationText.textContent = `Grid: [${data.location.x}, ${data.location.y}]`;
    terrainText.innerHTML = `<strong>${data.current_terrain.name.replace(/_/g, ' ')}</strong>: ${data.current_terrain.description}`;
    
    terrainList.innerHTML = data.visible_terrains.map(t => `
        <span class="terrain-badge" style="background-color: ${t.color}; color: ${getContrastColor(t.color)}">
            ${t.name.replace(/_/g, ' ')}
        </span>
    `).join('');
}

/**
 * Render observations panel
 */
function renderObservations(data, highlightId) {
    if (!data || data.observations.length === 0) {
        observationsList.innerHTML = '<p class="placeholder">No notable species observed here. Keep exploring...</p>';
        return;
    }
    
    let speciesToShow = data.observations;
    
    if (highlightId !== null) {
        speciesToShow = data.observations.filter(sp => sp.id === highlightId);
    } else {
        speciesToShow = data.observations.slice(0, 3);
    }
    
    if (speciesToShow.length === 0) {
        observationsList.innerHTML = '<p class="placeholder">Hover over species symbols on map to observe...</p>';
        return;
    }
    
    observationsList.innerHTML = speciesToShow.map(sp => `
        <div class="species-card ${highlightId === sp.id ? 'highlighted' : ''}">
            <div class="species-header">
                <span class="species-symbol">${SPECIES_SYMBOLS[sp.category] || '?'}</span>
                <h3>${sp.common_name}</h3>
                <span class="latin-name">${sp.latin_name}</span>
                <span class="category-badge ${sp.category}">${sp.category.replace(/_/g, ' ')}</span>
            </div>
            ${sp.photo_url ? `<img src="${sp.photo_url}" alt="${sp.common_name}" class="species-photo" onerror="this.style.display='none'">` : ''}
            <div class="species-details">
                <p><strong>Visual:</strong> ${sp.visual}</p>
                <p><strong>Touch:</strong> ${sp.tactile}</p>
                <p><strong>Smell:</strong> ${sp.smell}</p>
                <p><strong>Sound:</strong> ${sp.sound}</p>
                <p><strong>Habitat:</strong> ${sp.habitat}</p>
                <p><strong>Season:</strong> ${sp.season_note}</p>
                <p><strong>Uses:</strong> ${sp.uses}</p>
            </div>
        </div>
    `).join('');
    
    if (highlightId === null && data.observations.length > 3) {
        observationsList.innerHTML += `
            <p class="more-species">+ ${data.observations.length - 3} more species nearby. Hover on map to explore.</p>
        `;
    }
}

/**
 * Get contrasting text color for background
 */
function getContrastColor(hexcolor) {
    const r = parseInt(hexcolor.slice(1, 3), 16);
    const g = parseInt(hexcolor.slice(3, 5), 16);
    const b = parseInt(hexcolor.slice(5, 7), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? '#000000' : '#ffffff';
}

// Start the game
init();
