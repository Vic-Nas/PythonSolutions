console.log('Script loaded');

// State
const state = {
    platforms: [],
    folderCache: {},
    currentView: 'loading',
    currentPath: [],
    currentItem: null
};

// Utility
function getRepoPath() {
    const parts = window.location.pathname.split('/');
    return parts[1] && parts[2] ? `${parts[1]}/${parts[2]}` : 'Vic-Nas/PythonSolutions';
}

// Fetch folder contents
async function fetchFolderContents(path) {
    if (state.folderCache[path]) {
        return state.folderCache[path];
    }
    
    try {
        const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${path}`);
        if (!res.ok) return null;
        
        const items = await res.json();
        state.folderCache[path] = items;
        return items;
    } catch (err) {
        console.error(`Error fetching ${path}:`, err);
        return null;
    }
}

// Check if folder contains files (is a "problem")
function hasFiles(items) {
    return items.some(item => 
        item.type === 'file' && 
        (item.name.endsWith('.vn.py') || 
         item.name.endsWith('.vn.png') || 
         item.name.endsWith('.html'))
    );
}

// Load all platforms
async function loadPlatforms() {
    console.log('Loading platforms...');
    const rootItems = await fetchFolderContents('');
    if (!rootItems) return;
    
    const platformFolders = rootItems.filter(item => 
        item.type === 'dir' && 
        !['utils', '.git'].includes(item.name) &&
        !item.name.startsWith('.')
    );
    
    for (const folder of platformFolders) {
        const platformData = {
            name: folder.name,
            path: folder.name,
            image: null,
            count: 0
        };
        
        // Check for platform.png
        const contents = await fetchFolderContents(folder.name);
        if (contents) {
            const platformImg = contents.find(f => f.name === 'platform.png');
            if (platformImg) {
                // Use the download_url from GitHub API
                platformData.image = platformImg.download_url || `${folder.name}/platform.png`;
            }
            
            // Count items recursively
            platformData.count = await countItems(folder.name);
        }
        
        state.platforms.push(platformData);
    }
    
    state.platforms.sort((a, b) => a.name.localeCompare(b.name));
    console.log('Loaded platforms:', state.platforms);
}

// Recursively count problem items
async function countItems(path) {
    const items = await fetchFolderContents(path);
    if (!items) return 0;
    
    if (hasFiles(items)) return 1;
    
    const subdirs = items.filter(i => i.type === 'dir');
    let count = 0;
    
    for (const dir of subdirs) {
        count += await countItems(`${path}/${dir.name}`);
    }
    
    return count;
}

// Parse hash to navigate
function parseHash() {
    let hash = window.location.hash.slice(1);
    hash = decodeURIComponent(hash);
    
    console.log('Parsing hash:', hash);
    
    if (!hash) {
        return { view: 'platforms', path: [] };
    }
    
    // Check if it's a problem view
    if (hash.startsWith('view/')) {
        const pathStr = hash.slice(5);
        const path = pathStr.split('/');
        return { view: 'problem', path };
    }
    
    // Otherwise it's a folder navigation
    const path = hash.split('/');
    return { view: 'folder', path };
}

// Render views
function render() {
    console.log('Rendering view:', state.currentView, 'path:', state.currentPath);
    
    const views = ['loading-screen', 'platform-selector', 'folder-view', 'problem-view'];
    views.forEach(v => document.getElementById(v).style.display = 'none');
    
    if (state.currentView === 'loading') {
        document.getElementById('loading-screen').style.display = 'flex';
    } else if (state.currentView === 'platforms') {
        renderPlatforms();
    } else if (state.currentView === 'folder') {
        renderFolder();
    } else if (state.currentView === 'problem') {
        renderProblem();
    }
}

function renderPlatforms() {
    document.getElementById('platform-selector').style.display = 'block';
    const grid = document.getElementById('platform-grid');
    grid.innerHTML = '';
    
    state.platforms.forEach(platform => {
        const card = document.createElement('button');
        card.className = 'platform-box';
        card.dataset.platform = platform.name;
        
        const displayName = capitalize(platform.name);
        const countText = platform.name === 'vicutils' ? 'scripts' : 'problems';
        
        card.innerHTML = `
            ${platform.image ? 
                `<img src="${platform.image}" alt="${displayName}" class="platform-image">` :
                `<span class="platform-emoji">${getDefaultEmoji(platform.name)}</span>`
            }
            <h2>${displayName}</h2>
            <p>${platform.count} ${countText}</p>
        `;
        
        card.onclick = () => navigateTo([platform.name]);
        grid.appendChild(card);
    });
}

async function renderFolder() {
    const view = document.getElementById('folder-view');
    view.style.display = 'block';
    
    const pathStr = state.currentPath.join('/');
    const items = await fetchFolderContents(pathStr);
    
    if (!items) {
        view.innerHTML = '<p>Error loading folder</p>';
        return;
    }
    
    // Get subdirectories only
    const subdirs = items.filter(i => i.type === 'dir');
    
    // Set title
    const titleParts = state.currentPath.map(capitalize);
    document.getElementById('folder-title').textContent = titleParts.join(' / ');
    
    // Render cards
    const container = document.getElementById('folder-cards');
    container.innerHTML = '';
    
    for (const dir of subdirs) {
        const card = document.createElement('div');
        card.className = 'folder-card';
        
        const fullPath = [...state.currentPath, dir.name];
        const count = await countItems(fullPath.join('/'));
        
        card.innerHTML = `
            <div class="folder-card-title">${dir.name}</div>
            <div class="folder-card-path">${fullPath.join('/')}</div>
            <div class="folder-card-count">${count} item${count !== 1 ? 's' : ''}</div>
        `;
        
        card.onclick = () => navigateTo(fullPath);
        container.appendChild(card);
    }
}

async function renderProblem() {
    const view = document.getElementById('problem-view');
    view.style.display = 'block';
    view.innerHTML = '<div style="text-align: center; padding: 3rem;">Loading...</div>';
    
    const pathStr = state.currentPath.join('/');
    const items = await fetchFolderContents(pathStr);
    
    if (!items) {
        view.innerHTML = '<p>Error loading problem</p>';
        return;
    }
    
    // Separate files
    const htmlFiles = items.filter(f => f.type === 'file' && f.name.endsWith('.html'));
    const pngFiles = items.filter(f => 
        f.type === 'file' && 
        (f.name.endsWith('.vn.png') || f.name.match(/\.vn\.\d+\.png$/))
    ).sort((a, b) => {
        const numA = a.name.match(/\.(\d+)\.png$/)?.[1] || 0;
        const numB = b.name.match(/\.(\d+)\.png$/)?.[1] || 0;
        return parseInt(numA) - parseInt(numB);
    });
    const pyFiles = items.filter(f => 
        f.type === 'file' && 
        f.name.endsWith('.vn.py') && 
        !f.name.includes('.shortest.')
    );
    
    // Check if has HTML - if so, redirect
    if (htmlFiles.length > 0) {
        window.location.href = `${pathStr}/${htmlFiles[0].name}`;
        return;
    }
    
    // Fetch Python code
    let pythonCode = '';
    let problemUrl = '';
    
    if (pyFiles.length > 0) {
        try {
            const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${pathStr}/${pyFiles[0].name}`);
            if (res.ok) {
                const data = await res.json();
                pythonCode = atob(data.content);
                const match = pythonCode.match(/^#.*?(https:\/\/[^\s]+)/m);
                if (match) problemUrl = match[1];
            }
        } catch (err) {
            console.error('Error fetching Python code:', err);
        }
    }
    
    // Build HTML
    const problemName = state.currentPath[state.currentPath.length - 1];
    const title = problemName.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const subtitle = state.currentPath.slice(0, -1).map(capitalize).join(' / ');
    
    const repoUrl = `https://github.com/${getRepoPath()}/tree/main/${pathStr}`;
    
    let html = `
        <div class="problem-header">
            <div class="problem-nav">
                <a href="javascript:history.back()" class="nav-link">← Back</a>
                <a href="#" class="nav-link">🏠 Home</a>
                ${problemUrl ? `<a href="${problemUrl}" target="_blank" class="nav-link">🔗 Problem</a>` : ''}
                <a href="${repoUrl}" target="_blank" class="nav-link">📂 GitHub</a>
            </div>
            <h1 class="problem-title">${title}</h1>
            <p class="problem-subtitle">${subtitle}</p>
        </div>
    `;
    
    const hasSingleImage = pngFiles.length === 1;
    const hasCode = pythonCode.length > 0;
    
    if (hasSingleImage && hasCode) {
        // Side-by-side layout
        html += '<div class="content-wrapper">';
        
        html += '<div class="visual-panel">';
        html += `
            <div class="image-box">
                <img src="${pathStr}/${pngFiles[0].name}" alt="Solution">
                <div class="image-label">Solution Visualization</div>
            </div>
        `;
        html += '</div>';
        
        html += '<div class="code-panel">';
        html += `
            <div class="code-box">
                <div class="code-header">Python Solution</div>
                <div class="code-wrapper"><pre><code class="language-python">${escapeHtml(pythonCode)}</code></pre></div>
            </div>
        `;
        html += '</div>';
        
        html += '</div>';
    } else {
        // Stacked layout
        html += '<div class="content-wrapper stacked">';
        
        if (pngFiles.length > 0) {
            if (pngFiles.length === 1) {
                html += `
                    <div class="image-box">
                        <img src="${pathStr}/${pngFiles[0].name}" alt="Solution">
                        <div class="image-label">Solution Visualization</div>
                    </div>
                `;
            } else {
                html += '<div class="multi-image-grid">';
                pngFiles.forEach((img, i) => {
                    html += `
                        <div class="image-box">
                            <img src="${pathStr}/${img.name}" alt="Step ${i + 1}">
                            <div class="image-label">Step ${i + 1}</div>
                        </div>
                    `;
                });
                html += '</div>';
            }
        }
        
        if (hasCode) {
            html += `
                <div class="code-box">
                    <div class="code-header">Python Solution</div>
                    <div class="code-wrapper"><pre><code class="language-python">${escapeHtml(pythonCode)}</code></pre></div>
                </div>
            `;
        }
        
        html += '</div>';
    }
    
    view.innerHTML = html;
    hljs.highlightAll();
}

// Navigation
async function navigateTo(path) {
    console.log('Navigating to:', path);
    
    const pathStr = path.join('/');
    const items = await fetchFolderContents(pathStr);
    
    if (!items) {
        console.error('Could not load path:', pathStr);
        return;
    }
    
    // Check if this folder has files (is a problem)
    if (hasFiles(items)) {
        window.location.hash = `view/${path.map(encodeURIComponent).join('/')}`;
    } else {
        window.location.hash = path.map(encodeURIComponent).join('/');
    }
}

// Utilities
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getDefaultEmoji(platformName) {
    const emojis = {
        leetcode: '💡',
        kattis: '🎯',
        vicutils: '🔧',
        aoc: '🎄'
    };
    return emojis[platformName.toLowerCase()] || '📁';
}

// Event listeners
document.getElementById('back-button')?.addEventListener('click', () => {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.hash = '';
    }
});

window.addEventListener('hashchange', async () => {
    console.log('Hash changed');
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPath = parsed.path;
    render();
});

// Initialize
(async () => {
    console.log('Initializing app...');
    
    const isIndexPage = window.location.pathname.endsWith('index.html') || 
                        window.location.pathname.endsWith('/') || 
                        window.location.pathname.split('/').pop() === '';
    
    if (!isIndexPage) {
        console.log('Not index page, skipping initialization');
        return;
    }
    console.log('Script loaded');

// State
const state = {
    platforms: [],
    folderCache: {},
    currentView: 'loading',
    currentPath: [],
    currentItem: null
};

// Utility
function getRepoPath() {
    const parts = window.location.pathname.split('/');
    return parts[1] && parts[2] ? `${parts[1]}/${parts[2]}` : 'Vic-Nas/PythonSolutions';
}

// Fetch folder contents
async function fetchFolderContents(path) {
    if (state.folderCache[path]) {
        return state.folderCache[path];
    }
    
    try {
        const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${path}`);
        if (!res.ok) return null;
        
        const items = await res.json();
        state.folderCache[path] = items;
        return items;
    } catch (err) {
        console.error(`Error fetching ${path}:`, err);
        return null;
    }
}

// Check if folder contains files (is a "problem")
function hasFiles(items) {
    return items.some(item => 
        item.type === 'file' && 
        (item.name.endsWith('.vn.py') || 
         item.name.endsWith('.vn.png') || 
         item.name.endsWith('.html'))
    );
}

// Load all platforms
async function loadPlatforms() {
    console.log('Loading platforms...');
    const rootItems = await fetchFolderContents('');
    if (!rootItems) return;
    
    const platformFolders = rootItems.filter(item => 
        item.type === 'dir' && 
        !['utils', '.git'].includes(item.name) &&
        !item.name.startsWith('.')
    );
    
    for (const folder of platformFolders) {
        const platformData = {
            name: folder.name,
            path: folder.name,
            image: null,
            count: 0
        };
        
        // Check for platform.png
        const contents = await fetchFolderContents(folder.name);
        if (contents) {
            const platformImg = contents.find(f => f.name === 'platform.png');
            if (platformImg) {
                // Use the download_url from GitHub API
                platformData.image = platformImg.download_url || `${folder.name}/platform.png`;
            }
            
            // Count items recursively
            platformData.count = await countItems(folder.name);
        }
        
        state.platforms.push(platformData);
    }
    
    state.platforms.sort((a, b) => a.name.localeCompare(b.name));
    console.log('Loaded platforms:', state.platforms);
}

// Recursively count problem items
async function countItems(path) {
    const items = await fetchFolderContents(path);
    if (!items) return 0;
    
    if (hasFiles(items)) return 1;
    
    const subdirs = items.filter(i => i.type === 'dir');
    let count = 0;
    
    for (const dir of subdirs) {
        count += await countItems(`${path}/${dir.name}`);
    }
    
    return count;
}

// Parse hash to navigate
function parseHash() {
    let hash = window.location.hash.slice(1);
    hash = decodeURIComponent(hash);
    
    console.log('Parsing hash:', hash);
    
    if (!hash) {
        return { view: 'platforms', path: [] };
    }
    
    // Check if it's a problem view
    if (hash.startsWith('view/')) {
        const pathStr = hash.slice(5);
        const path = pathStr.split('/');
        return { view: 'problem', path };
    }
    
    // Otherwise it's a folder navigation
    const path = hash.split('/');
    return { view: 'folder', path };
}

// Render views
function render() {
    console.log('Rendering view:', state.currentView, 'path:', state.currentPath);
    
    const views = ['loading-screen', 'platform-selector', 'folder-view', 'problem-view'];
    views.forEach(v => document.getElementById(v).style.display = 'none');
    
    if (state.currentView === 'loading') {
        document.getElementById('loading-screen').style.display = 'flex';
    } else if (state.currentView === 'platforms') {
        renderPlatforms();
    } else if (state.currentView === 'folder') {
        renderFolder();
    } else if (state.currentView === 'problem') {
        renderProblem();
    }
}

function renderPlatforms() {
    document.getElementById('platform-selector').style.display = 'block';
    const grid = document.getElementById('platform-grid');
    grid.innerHTML = '';
    
    state.platforms.forEach(platform => {
        const card = document.createElement('button');
        card.className = 'platform-box';
        card.dataset.platform = platform.name;
        
        const displayName = capitalize(platform.name);
        const countText = platform.name === 'vicutils' ? 'scripts' : 'problems';
        
        card.innerHTML = `
            ${platform.image ? 
                `<img src="${platform.image}" alt="${displayName}" class="platform-image">` :
                `<span class="platform-emoji">${getDefaultEmoji(platform.name)}</span>`
            }
            <h2>${displayName}</h2>
            <p>${platform.count} ${countText}</p>
        `;
        
        card.onclick = () => navigateTo([platform.name]);
        grid.appendChild(card);
    });
}

async function renderFolder() {
    const view = document.getElementById('folder-view');
    view.style.display = 'block';
    
    const pathStr = state.currentPath.join('/');
    const items = await fetchFolderContents(pathStr);
    
    if (!items) {
        view.innerHTML = '<p>Error loading folder</p>';
        return;
    }
    
    // Get subdirectories only
    const subdirs = items.filter(i => i.type === 'dir');
    
    // Set title
    const titleParts = state.currentPath.map(capitalize);
    document.getElementById('folder-title').textContent = titleParts.join(' / ');
    
    // Render cards
    const container = document.getElementById('folder-cards');
    container.innerHTML = '';
    
    for (const dir of subdirs) {
        const card = document.createElement('div');
        card.className = 'folder-card';
        
        const fullPath = [...state.currentPath, dir.name];
        const count = await countItems(fullPath.join('/'));
        
        card.innerHTML = `
            <div class="folder-card-title">${dir.name}</div>
            <div class="folder-card-path">${fullPath.join('/')}</div>
            <div class="folder-card-count">${count} item${count !== 1 ? 's' : ''}</div>
        `;
        
        card.onclick = () => navigateTo(fullPath);
        container.appendChild(card);
    }
}

async function renderProblem() {
    const view = document.getElementById('problem-view');
    view.style.display = 'block';
    view.innerHTML = '<div style="text-align: center; padding: 3rem;">Loading...</div>';
    
    const pathStr = state.currentPath.join('/');
    const items = await fetchFolderContents(pathStr);
    
    if (!items) {
        view.innerHTML = '<p>Error loading problem</p>';
        return;
    }
    
    // Separate files
    const htmlFiles = items.filter(f => f.type === 'file' && f.name.endsWith('.html'));
    const pngFiles = items.filter(f => 
        f.type === 'file' && 
        (f.name.endsWith('.vn.png') || f.name.match(/\.vn\.\d+\.png$/))
    ).sort((a, b) => {
        const numA = a.name.match(/\.(\d+)\.png$/)?.[1] || 0;
        const numB = b.name.match(/\.(\d+)\.png$/)?.[1] || 0;
        return parseInt(numA) - parseInt(numB);
    });
    const pyFiles = items.filter(f => 
        f.type === 'file' && 
        f.name.endsWith('.vn.py') && 
        !f.name.includes('.shortest.')
    );
    
    // Check if has HTML - if so, redirect
    if (htmlFiles.length > 0) {
        window.location.href = `${pathStr}/${htmlFiles[0].name}`;
        return;
    }
    
    // Fetch Python code
    let pythonCode = '';
    let problemUrl = '';
    
    if (pyFiles.length > 0) {
        try {
            const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${pathStr}/${pyFiles[0].name}`);
            if (res.ok) {
                const data = await res.json();
                pythonCode = atob(data.content);
                const match = pythonCode.match(/^#.*?(https:\/\/[^\s]+)/m);
                if (match) problemUrl = match[1];
            }
        } catch (err) {
            console.error('Error fetching Python code:', err);
        }
    }
    
    // Build HTML
    const problemName = state.currentPath[state.currentPath.length - 1];
    const title = problemName.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const subtitle = state.currentPath.slice(0, -1).map(capitalize).join(' / ');
    
    const repoUrl = `https://github.com/${getRepoPath()}/tree/main/${pathStr}`;
    
    let html = `
        <div class="problem-header">
            <div class="problem-nav">
                <a href="javascript:history.back()" class="nav-link">← Back</a>
                <a href="#" class="nav-link">🏠 Home</a>
                ${problemUrl ? `<a href="${problemUrl}" target="_blank" class="nav-link">🔗 Problem</a>` : ''}
                <a href="${repoUrl}" target="_blank" class="nav-link">📂 GitHub</a>
            </div>
            <h1 class="problem-title">${title}</h1>
            <p class="problem-subtitle">${subtitle}</p>
        </div>
    `;
    
    const hasSingleImage = pngFiles.length === 1;
    const hasCode = pythonCode.length > 0;
    
    if (hasSingleImage && hasCode) {
        // Side-by-side layout
        html += '<div class="content-wrapper">';
        
        html += '<div class="visual-panel">';
        html += `
            <div class="image-box">
                <img src="${pathStr}/${pngFiles[0].name}" alt="Solution">
                <div class="image-label">Solution Visualization</div>
            </div>
        `;
        html += '</div>';
        
        html += '<div class="code-panel">';
        html += `
            <div class="code-box">
                <div class="code-header">Python Solution</div>
                <div class="code-wrapper"><pre><code class="language-python">${escapeHtml(pythonCode)}</code></pre></div>
            </div>
        `;
        html += '</div>';
        
        html += '</div>';
    } else {
        // Stacked layout
        html += '<div class="content-wrapper stacked">';
        
        if (pngFiles.length > 0) {
            if (pngFiles.length === 1) {
                html += `
                    <div class="image-box">
                        <img src="${pathStr}/${pngFiles[0].name}" alt="Solution">
                        <div class="image-label">Solution Visualization</div>
                    </div>
                `;
            } else {
                html += '<div class="multi-image-grid">';
                pngFiles.forEach((img, i) => {
                    html += `
                        <div class="image-box">
                            <img src="${pathStr}/${img.name}" alt="Step ${i + 1}">
                            <div class="image-label">Step ${i + 1}</div>
                        </div>
                    `;
                });
                html += '</div>';
            }
        }
        
        if (hasCode) {
            html += `
                <div class="code-box">
                    <div class="code-header">Python Solution</div>
                    <div class="code-wrapper"><pre><code class="language-python">${escapeHtml(pythonCode)}</code></pre></div>
                </div>
            `;
        }
        
        html += '</div>';
    }
    
    view.innerHTML = html;
    hljs.highlightAll();
}

// Navigation
async function navigateTo(path) {
    console.log('Navigating to:', path);
    
    const pathStr = path.join('/');
    const items = await fetchFolderContents(pathStr);
    
    if (!items) {
        console.error('Could not load path:', pathStr);
        return;
    }
    
    // Check if this folder has files (is a problem)
    if (hasFiles(items)) {
        window.location.hash = `view/${path.map(encodeURIComponent).join('/')}`;
    } else {
        window.location.hash = path.map(encodeURIComponent).join('/');
    }
}

function goBack() {
    console.log('Going back from:', state.currentPath);
    
    // If we're viewing a problem, go back to its parent folder
    if (state.currentView === 'problem') {
        if (state.currentPath.length > 1) {
            // Go to parent folder
            const parentPath = state.currentPath.slice(0, -1);
            window.location.hash = parentPath.map(encodeURIComponent).join('/');
        } else {
            // Go to home
            window.location.hash = '';
        }
    } 
    // If we're in a folder view, go back one level
    else if (state.currentView === 'folder') {
        if (state.currentPath.length > 1) {
            // Go to parent folder
            const parentPath = state.currentPath.slice(0, -1);
            window.location.hash = parentPath.map(encodeURIComponent).join('/');
        } else {
            // Go to home
            window.location.hash = '';
        }
    }
    // Otherwise go home
    else {
        window.location.hash = '';
    }
}

// Utilities
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getDefaultEmoji(platformName) {
    const emojis = {
        leetcode: '💡',
        kattis: '🎯',
        vicutils: '🔧',
        aoc: '🎄'
    };
    return emojis[platformName.toLowerCase()] || '📁';
}

// Event listeners
document.getElementById('back-button')?.addEventListener('click', () => {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.hash = '';
    }
});

window.addEventListener('hashchange', async () => {
    console.log('Hash changed');
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPath = parsed.path;
    render();
});

// Initialize
(async () => {
    console.log('Initializing app...');
    
    const isIndexPage = window.location.pathname.endsWith('index.html') || 
                        window.location.pathname.endsWith('/') || 
                        window.location.pathname.split('/').pop() === '';
    
    if (!isIndexPage) {
        console.log('Not index page, skipping initialization');
        return;
    }
    
    await loadPlatforms();
    
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPath = parsed.path;
    
    console.log('Initial state:', state);
    
    render();
})();
    await loadPlatforms();
    
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPath = parsed.path;
    
    console.log('Initial state:', state);
    
    render();
})();