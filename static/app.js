/**
 * Star Carr Mesolithic Scholar Simulator - Game Engine
 * With god mode, revealed cells memory, and corridor visualization.
 */

// Game state
const state = {
    config: null,
    playerX: 0,
    playerY: 0,
    currentObservations: null,
    revealedCells: new Set(), // Persists during session
    godMode: false,
    showCorridors: true,
    showSigns: true,
    showAllTerrain: false,
    corridorData: null,
    allSignsData: null,
    timeOfDay: 'midday'
};

// Canvas setup
const canvas = document.getElementById('map-canvas');
const ctx = canvas.getContext('2d');
const CELL_SIZE = 8;
const VIEW_RADIUS = 25;

// Species category symbols
const SPECIES_SYMBOLS = {
    'tree': '🌳',
    'shrub': '🌿',
    'plant': '🌱',
    'large_herbivore': '🦌',
    'medium_herbivore': '🦫',
    'predator': '🐺',
    'aquatic': '🐟'
};

// DOM elements
const locationText = document.getElementById('location-text');
const terrainText = document.getElementById('terrain-text');
const corridorText = document.getElementById('corridor-text');
const terrainList = document.getElementById('terrain-list');
const signsList = document.getElementById('signs-list');
const observationsList = document.getElementById('observations-list');
const godModeCheckbox = document.getElementById('god-mode-checkbox');
const godModePanel = document.getElementById('god-mode-panel');
const showCorridorsCheckbox = document.getElementById('show-corridors');
const showSignsCheckbox = document.getElementById('show-signs');
const showAllTerrainCheckbox = document.getElementById('show-all-terrain');
const timeSelect = document.getElementById('time-select');
const corridorLegend = document.getElementById('corridor-legend');
const predatorInfo = document.getElementById('predator-info');

/**
 * Initialize the game
 */
async function init() {
    try {
        const response = await fetch('/api/config');
        state.config = await response.json();
        
        state.playerX = state.config.spawn_x;
        state.playerY = state.config.spawn_y;
        state.timeOfDay = state.config.time_of_day || 'midday';
        
        timeSelect.value = state.timeOfDay;
        
        setupControls();
        await updateView();
        
        // Show predator presence in god mode
        updatePredatorInfo();
        
        console.log('Star Carr initialized', state.config);
    } catch (error) {
        console.error('Failed to initialize:', error);
        locationText.textContent = 'Error loading game. Check console.';
    }
}

/**
 * Setup all controls
 */
function setupControls() {
    // Keyboard movement
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
    
    // Mouse click
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
    
    // God mode toggle
    godModeCheckbox.addEventListener('change', async (e) => {
        state.godMode = e.target.checked;
        godModePanel.classList.toggle('hidden', !state.godMode);
        
        if (state.godMode && !state.corridorData) {
            await loadGodModeData();
        }
        
        renderMap(state.lastTerrainData);
    });
    
    // God mode options
    showCorridorsCheckbox.addEventListener('change', (e) => {
        state.showCorridors = e.target.checked;
        renderMap(state.lastTerrainData);
    });
    
    showSignsCheckbox.addEventListener('change', (e) => {
        state.showSigns = e.target.checked;
        renderMap(state.lastTerrainData);
    });
    
    showAllTerrainCheckbox.addEventListener('change', (e) => {
        state.showAllTerrain = e.target.checked;
        renderMap(state.lastTerrainData);
    });
    
    // Time selector
    timeSelect.addEventListener('change', async (e) => {
        state.timeOfDay = e.target.value;
        
        await fetch('/api/time', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({time_of_day: state.timeOfDay})
        });
        
        await updateView();
    });
}

/**
 * Load god mode data (corridors, all signs)
 */
async function loadGodModeData() {
    try {
        const [corridorRes, signsRes] = await Promise.all([
            fetch('/api/god_mode/corridors'),
            fetch('/api/god_mode/signs')
        ]);
        
        state.corridorData = await corridorRes.json();
        state.allSignsData = await signsRes.json();
        
        // Build corridor legend
        buildCorridorLegend();
    } catch (error) {
        console.error('Failed to load god mode data:', error);
    }
}

/**
 * Build corridor legend in god mode panel
 */
function buildCorridorLegend() {
    if (!state.corridorData) return;
    
    let html = '<h4>Corridors</h4>';
    for (const [name, data] of Object.entries(state.corridorData)) {
        html += `<div class="legend-item">
            <span class="legend-color" style="background:${data.color}"></span>
            ${name.replace('_', ' ')} (${data.count} cells)
        </div>`;
    }
    corridorLegend.innerHTML = html;
}

/**
 * Update predator presence info
 */
function updatePredatorInfo() {
    if (!state.config?.predator_presence) return;
    
    let html = '<h4>Predator Presence</h4>';
    for (const [species, present] of Object.entries(state.config.predator_presence)) {
        if (species === 'wolf' || species === 'bear') {
            const status = present ? '⚠️ PRESENT' : '✓ absent';
            const cls = present ? 'present' : 'absent';
            html += `<div class="predator-item ${cls}">${species}: ${status}</div>`;
        }
    }
    predatorInfo.innerHTML = html;
}

/**
 * Move player
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
    
    // Mark cells as revealed
    const visRadius = state.config.visibility_radius;
    for (let dy2 = -visRadius; dy2 <= visRadius; dy2++) {
        for (let dx2 = -visRadius; dx2 <= visRadius; dx2++) {
            if (dx2*dx2 + dy2*dy2 <= visRadius*visRadius) {
                const ry = newY + dy2;
                const rx = newX + dx2;
                if (rx >= 0 && rx < state.config.grid_cols &&
                    ry >= 0 && ry < state.config.grid_rows) {
                    state.revealedCells.add(`${rx},${ry}`);
                }
            }
        }
    }
    
    await updateView();
}

/**
 * Fetch terrain batch
 */
async function fetchTerrainBatch(minX, minY, maxX, maxY) {
    const url = `/api/terrain_batch?min_x=${minX}&min_y=${minY}&max_x=${maxX}&max_y=${maxY}`;
    const response = await fetch(url);
    return await response.json();
}

/**
 * Fetch observations
 */
async function fetchObservations() {
    const url = `/api/observe/${state.playerX}/${state.playerY}`;
    const response = await fetch(url);
    return await response.json();
}

/**
 * Update entire view
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
    
    state.lastTerrainData = terrainData;
    state.currentObservations = observations;
    
    renderMap(terrainData);
    renderObservations(observations);
}

/**
 * Render map with god mode overlays
 */
function renderMap(terrainData) {
    if (!terrainData) return;
    
    const { min_x, min_y, cells } = terrainData;
    const visRadius = state.config.visibility_radius;
    
    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Calculate offset
    const offsetX = canvas.width / 2 - (state.playerX - min_x) * CELL_SIZE - CELL_SIZE / 2;
    const offsetY = canvas.height / 2 - (state.playerY - min_y) * CELL_SIZE - CELL_SIZE / 2;
    
    // Draw terrain
    for (let row = 0; row < cells.length; row++) {
        for (let col = 0; col < cells[row].length; col++) {
            const worldX = min_x + col;
            const worldY = min_y + row;
            
            const dx = worldX - state.playerX;
            const dy = worldY - state.playerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            const screenX = offsetX + col * CELL_SIZE;
            const screenY = offsetY + row * CELL_SIZE;
            
            const isVisible = dist <= visRadius;
            const isRevealed = state.revealedCells.has(`${worldX},${worldY}`);
            const showAll = state.godMode && state.showAllTerrain;
            
            if (isVisible || isRevealed || showAll) {
                const terrainId = cells[row][col];
                const terrain = state.config.terrain_types[terrainId];
                let color = terrain ? terrain.color : '#888';
                
                // Dim revealed but not visible cells
                if (!isVisible && isRevealed && !showAll) {
                    color = dimColor(color, 0.6);
                }
                
                ctx.fillStyle = color;
            } else {
                ctx.fillStyle = '#2a2a3e';
            }
            
            ctx.fillRect(screenX, screenY, CELL_SIZE - 1, CELL_SIZE - 1);
        }
    }
    
    // God mode: Draw corridors
    if (state.godMode && state.showCorridors && state.corridorData) {
        for (const [name, data] of Object.entries(state.corridorData)) {
            ctx.fillStyle = data.color;
            
            for (const [cx, cy] of data.cells) {
                const screenX = offsetX + (cx - min_x) * CELL_SIZE;
                const screenY = offsetY + (cy - min_y) * CELL_SIZE;
                
                if (screenX >= -CELL_SIZE && screenX < canvas.width + CELL_SIZE &&
                    screenY >= -CELL_SIZE && screenY < canvas.height + CELL_SIZE) {
                    ctx.fillRect(screenX + 1, screenY + 1, CELL_SIZE - 3, CELL_SIZE - 3);
                }
            }
        }
    }
    
    // God mode: Draw all signs
    if (state.godMode && state.showSigns && state.allSignsData) {
        ctx.font = `${CELL_SIZE}px monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        for (const signType of state.allSignsData) {
            ctx.fillStyle = signType.color;
            
            for (const loc of signType.locations) {
                const screenX = offsetX + (loc.x - min_x) * CELL_SIZE + CELL_SIZE / 2;
                const screenY = offsetY + (loc.y - min_y) * CELL_SIZE + CELL_SIZE / 2;
                
                if (screenX >= 0 && screenX < canvas.width &&
                    screenY >= 0 && screenY < canvas.height) {
                    ctx.fillText(signType.char, screenX, screenY);
                }
            }
        }
    }
    
    // Draw visible signs (non-god mode or overlay)
    // Also draw previously revealed signs
    ctx.font = `${CELL_SIZE + 2}px monospace`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Draw all revealed signs (persistent)
    for (const sign of state.revealedSigns) {
        const screenX = offsetX + (sign.x - min_x) * CELL_SIZE + CELL_SIZE / 2;
        const screenY = offsetY + (sign.y - min_y) * CELL_SIZE + CELL_SIZE / 2;
        
        if (screenX >= 0 && screenX < canvas.width &&
            screenY >= 0 && screenY < canvas.height) {
            ctx.fillStyle = sign.color;
            ctx.fillText(sign.char, screenX, screenY);
        }
    }
    
    // Add current visible signs to revealed set
    if (state.currentObservations?.signs) {
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        for (const sign of state.currentObservations.signs) {
            const screenX = offsetX + (sign.x - min_x) * CELL_SIZE + CELL_SIZE / 2;
            const screenY = offsetY + (sign.y - min_y) * CELL_SIZE + CELL_SIZE / 2;
            
            ctx.fillStyle = sign.color;
            ctx.fillText(sign.char, screenX, screenY);
        }
    }
    
    // Draw species symbols within visibility
    if (state.currentObservations?.observations) {
        const visRadius = state.config.visibility_radius;
        ctx.font = `${CELL_SIZE}px serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        for (const sp of state.currentObservations.observations) {
            if (!sp.locations) continue;
            
            const symbol = SPECIES_SYMBOLS[sp.category] || '?';
            
            for (const loc of sp.locations) {
                const dx = loc.x - state.playerX;
                const dy = loc.y - state.playerY;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist <= visRadius) {
                    const screenX = offsetX + (loc.x - min_x) * CELL_SIZE + CELL_SIZE / 2;
                    const screenY = offsetY + (loc.y - min_y) * CELL_SIZE + CELL_SIZE / 2;
                    ctx.fillText(symbol, screenX, screenY);
                }
            }
        }
    }
    
    // Draw player
    const playerScreenX = canvas.width / 2;
    const playerScreenY = canvas.height / 2;
    
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(playerScreenX, playerScreenY, CELL_SIZE / 2 + 2, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw visibility circle
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(playerScreenX, playerScreenY, visRadius * CELL_SIZE, 0, Math.PI * 2);
    ctx.stroke();
}

/**
 * Dim a hex color
 */
function dimColor(hex, factor) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    const dr = Math.floor(r * factor);
    const dg = Math.floor(g * factor);
    const db = Math.floor(b * factor);
    
    return `#${dr.toString(16).padStart(2, '0')}${dg.toString(16).padStart(2, '0')}${db.toString(16).padStart(2, '0')}`;
}

/**
 * Render observations panel
 */
function renderObservations(data) {
    // Location
    locationText.textContent = `Grid: [${data.location.x}, ${data.location.y}]`;
    terrainText.innerHTML = `<strong>${data.current_terrain.name.replace(/_/g, ' ')}</strong>`;
    
    // Corridor info
    if (data.corridors && data.corridors.length > 0) {
        corridorText.innerHTML = `📍 In corridor: ${data.corridors.map(c => c.replace(/_/g, ' ')).join(', ')}`;
        corridorText.classList.remove('hidden');
    } else {
        corridorText.classList.add('hidden');
    }
    
    // Visible terrains
    terrainList.innerHTML = data.visible_terrains.map(t => `
        <span class="terrain-badge" style="background-color: ${t.color}; color: ${getContrastColor(t.color)}">
            ${t.name.replace(/_/g, ' ')}
        </span>
    `).join('');
    
    // Signs
    if (data.signs && data.signs.length > 0) {
        const grouped = {};
        for (const sign of data.signs) {
            if (!grouped[sign.type]) {
                grouped[sign.type] = {...sign, count: 0};
            }
            grouped[sign.type].count++;
        }
        
        signsList.innerHTML = Object.values(grouped).map(s => `
            <div class="sign-item">
                <span class="sign-char" style="color: ${s.color}">${s.char}</span>
                <span class="sign-desc">${s.description} (×${s.count})</span>
            </div>
        `).join('');
    } else {
        signsList.innerHTML = '<p class="placeholder">No tracks or signs visible...</p>';
    }
    
    // Species observations
    if (data.observations.length === 0) {
        observationsList.innerHTML = '<p class="placeholder">No notable species observed here. Keep exploring...</p>';
        return;
    }
    
    observationsList.innerHTML = data.observations.map(sp => `
        <div class="species-card">
            <div class="species-header">
                <h3>${sp.common_name}</h3>
                <span class="latin-name">${sp.latin_name}</span>
                <span class="category-badge ${sp.category}">${sp.category.replace(/_/g, ' ')}</span>
                ${sp.state > 1 ? `<span class="state-badge">state: ${sp.state}</span>` : ''}
            </div>
            ${sp.photo_url ? `<img src="${sp.photo_url}" alt="${sp.common_name}" class="species-photo">` : ''}
            <div class="species-details">
                <p><strong>👁 Visual:</strong> ${sp.visual || ''}</p>
                <p><strong>✋ Touch:</strong> ${sp.tactile || ''}</p>
                <p><strong>👃 Smell:</strong> ${sp.smell || ''}</p>
                <p><strong>👂 Sound:</strong> ${sp.sound || ''}</p>
                <p><strong>🏠 Habitat:</strong> ${sp.habitat || ''}</p>
                <p><strong>🌸 Season:</strong> ${sp.season_note || ''}</p>
                <p><strong>🔧 Uses:</strong> ${sp.uses || ''}</p>
            </div>
        </div>
    `).join('');
}

/**
 * Get contrasting text color
 */
function getContrastColor(hexcolor) {
    const r = parseInt(hexcolor.slice(1, 3), 16);
    const g = parseInt(hexcolor.slice(3, 5), 16);
    const b = parseInt(hexcolor.slice(5, 7), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? '#000000' : '#ffffff';
}

// Start
init();
