/**
 * Star Carr Mesolithic Scholar Simulator - Game Engine
 */

// Game state
const state = {
    config: null,
    playerX: 0,
    playerY: 0,
    terrainCache: {},
    currentObservations: null,
    speciesMap: {} // species by cell: "x,y" -> species data
};

// Species category symbols
const CATEGORY_SYMBOLS = {
    tree: '🌲',
    shrub: '🌿',
    plant: '🌱',
    large_herbivore: '🦌',
    medium_herbivore: '🦫',
    predator: '🐺',
    aquatic: '🐟'
};

// Canvas setup
const canvas = document.getElementById('map-canvas');
const ctx = canvas.getContext('2d');
const CELL_SIZE = 16; // pixels per cell on screen (doubled)
const VIEW_RADIUS = 15; // cells to show around player (reduced)

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
        // Load config
        const response = await fetch('/api/config');
        state.config = await response.json();
        
        // Set player spawn
        state.playerX = state.config.spawn_x;
        state.playerY = state.config.spawn_y;
        
        // Setup controls
        setupControls();
        
        // Initial render
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
            case 'ArrowUp':
            case 'w':
            case 'W':
                dy = -1;
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                dy = 1;
                break;
            case 'ArrowLeft':
            case 'a':
            case 'A':
                dx = -1;
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                dx = 1;
                break;
            default:
                return;
        }
        
        e.preventDefault();
        movePlayer(dx, dy);
    });
    
    // Mouse click on canvas
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        // Convert to grid coordinates
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        const dx = Math.round((clickX - centerX) / CELL_SIZE);
        const dy = Math.round((clickY - centerY) / CELL_SIZE);
        
        if (dx !== 0 || dy !== 0) {
            // Move one step toward click
            const stepX = dx === 0 ? 0 : (dx > 0 ? 1 : -1);
            const stepY = dy === 0 ? 0 : (dy > 0 ? 1 : -1);
            movePlayer(stepX, stepY);
        }
    });
    
    // Hover tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'map-tooltip';
    tooltip.style.cssText = 'position:absolute;background:#1a1a2e;border:1px solid #86efac;padding:8px;border-radius:4px;display:none;pointer-events:none;z-index:100;font-size:0.85rem;max-width:200px;';
    document.body.appendChild(tooltip);
    
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Convert to world coordinates
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const dx = Math.round((mouseX - centerX) / CELL_SIZE);
        const dy = Math.round((mouseY - centerY) / CELL_SIZE);
        const worldX = state.playerX + dx;
        const worldY = state.playerY + dy;
        
        // Check if within visibility
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist <= state.config.visibility_radius) {
            const key = `${worldX},${worldY}`;
            const species = state.speciesMap[key];
            const terrainId = state.terrainCache[key];
            const terrain = state.config.terrain_types[terrainId];
            
            let html = `<strong>[${worldX}, ${worldY}]</strong><br>`;
            html += terrain ? terrain.name.replace('_', ' ') : 'unknown';
            if (species) {
                const symbol = CATEGORY_SYMBOLS[species.category] || '?';
                html += `<br>${symbol} ${species.common_name}`;
            }
            
            tooltip.innerHTML = html;
            tooltip.style.left = (e.clientX + 15) + 'px';
            tooltip.style.top = (e.clientY + 15) + 'px';
            tooltip.style.display = 'block';
        } else {
            tooltip.style.display = 'none';
        }
    });
    
    canvas.addEventListener('mouseout', () => {
        tooltip.style.display = 'none';
    });
}

/**
 * Move player by delta
 */
async function movePlayer(dx, dy) {
    const newX = state.playerX + dx;
    const newY = state.playerY + dy;
    
    // Bounds check
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
    // Fetch terrain for visible area
    const minX = Math.max(0, state.playerX - VIEW_RADIUS);
    const minY = Math.max(0, state.playerY - VIEW_RADIUS);
    const maxX = Math.min(state.config.grid_cols, state.playerX + VIEW_RADIUS + 1);
    const maxY = Math.min(state.config.grid_rows, state.playerY + VIEW_RADIUS + 1);
    
    const [terrainData, observations] = await Promise.all([
        fetchTerrainBatch(minX, minY, maxX, maxY),
        fetchObservations()
    ]);
    
    state.currentObservations = observations;
    
    // Build terrain cache
    for (let row = 0; row < terrainData.cells.length; row++) {
        for (let col = 0; col < terrainData.cells[row].length; col++) {
            const worldX = terrainData.min_x + col;
            const worldY = terrainData.min_y + row;
            state.terrainCache[`${worldX},${worldY}`] = terrainData.cells[row][col];
        }
    }
    
    // Build species map from observations
    state.speciesMap = {};
    for (const sp of observations.observations) {
        if (sp.locations) {
            for (const loc of sp.locations) {
                state.speciesMap[`${loc.x},${loc.y}`] = sp;
            }
        }
    }
    
    renderMap(terrainData);
    renderObservations(observations);
}

/**
 * Render the map canvas
 */
function renderMap(terrainData) {
    const { min_x, min_y, cells } = terrainData;
    const visRadius = state.config.visibility_radius;
    
    // Clear canvas
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Calculate offset to center player
    const offsetX = canvas.width / 2 - (state.playerX - min_x) * CELL_SIZE - CELL_SIZE / 2;
    const offsetY = canvas.height / 2 - (state.playerY - min_y) * CELL_SIZE - CELL_SIZE / 2;
    
    // Draw terrain cells
    for (let row = 0; row < cells.length; row++) {
        for (let col = 0; col < cells[row].length; col++) {
            const worldX = min_x + col;
            const worldY = min_y + row;
            
            // Check if in visibility radius
            const dx = worldX - state.playerX;
            const dy = worldY - state.playerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            const screenX = offsetX + col * CELL_SIZE;
            const screenY = offsetY + row * CELL_SIZE;
            
            if (dist <= visRadius) {
                // Visible - show terrain color
                const terrainId = cells[row][col];
                const terrain = state.config.terrain_types[terrainId];
                ctx.fillStyle = terrain ? terrain.color : '#888';
                ctx.fillRect(screenX, screenY, CELL_SIZE - 1, CELL_SIZE - 1);
                
                // Draw species symbol if present
                const key = `${worldX},${worldY}`;
                const species = state.speciesMap[key];
                if (species) {
                    const symbol = CATEGORY_SYMBOLS[species.category] || '?';
                    ctx.font = `${CELL_SIZE - 4}px sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(symbol, screenX + CELL_SIZE / 2, screenY + CELL_SIZE / 2);
                }
            } else {
                // Fog of war
                ctx.fillStyle = '#2a2a3e';
                ctx.fillRect(screenX, screenY, CELL_SIZE - 1, CELL_SIZE - 1);
            }
        }
    }
    
    // Draw player
    const playerScreenX = canvas.width / 2 - CELL_SIZE / 2;
    const playerScreenY = canvas.height / 2 - CELL_SIZE / 2;
    
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(playerScreenX + CELL_SIZE / 2, playerScreenY + CELL_SIZE / 2, CELL_SIZE / 2 + 2, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw visibility circle outline
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, visRadius * CELL_SIZE, 0, Math.PI * 2);
    ctx.stroke();
}

/**
 * Render observations panel
 */
function renderObservations(data) {
    // Update location
    locationText.textContent = `Grid: [${data.location.x}, ${data.location.y}]`;
    terrainText.innerHTML = `<strong>${data.current_terrain.name.replace('_', ' ')}</strong>: ${data.current_terrain.description}`;
    
    // Update visible terrains
    terrainList.innerHTML = data.visible_terrains.map(t => `
        <span class="terrain-badge" style="background-color: ${t.color}; color: ${getContrastColor(t.color)}">
            ${t.name.replace('_', ' ')}
        </span>
    `).join('');
    
    // Update observations
    if (data.observations.length === 0) {
        observationsList.innerHTML = '<p class="placeholder">No notable species observed here. Keep exploring...</p>';
        return;
    }
    
    observationsList.innerHTML = data.observations.map(sp => `
        <div class="species-card">
            <div class="species-header">
                <h3>${sp.common_name}</h3>
                <span class="latin-name">${sp.latin_name}</span>
                <span class="category-badge ${sp.category}">${sp.category.replace('_', ' ')}</span>
            </div>
            ${sp.photo_url ? `<img src="${sp.photo_url}" alt="${sp.common_name}" class="species-photo">` : ''}
            <div class="species-details">
                <p><strong>ðŸ‘ Visual:</strong> ${sp.visual}</p>
                <p><strong>âœ‹ Touch:</strong> ${sp.tactile}</p>
                <p><strong>ðŸ‘ƒ Smell:</strong> ${sp.smell}</p>
                <p><strong>ðŸ‘‚ Sound:</strong> ${sp.sound}</p>
                <p><strong>ðŸ  Habitat:</strong> ${sp.habitat}</p>
                <p><strong>ðŸŒ¸ Season:</strong> ${sp.season_note}</p>
                <p><strong>ðŸ”§ Uses:</strong> ${sp.uses}</p>
            </div>
        </div>
    `).join('');
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
