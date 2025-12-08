console.log('Script loaded');

// State
const state = {
    platforms: [],
    treeData: {},
    currentView: 'loading',
    currentPath: [],
    currentItem: null,
    pyodide: null,
    pyodideLoading: false,
    originalCode: '',
    uploadedFiles: [] // Track uploaded files
};

// Pyodide Management
async function initPyodide() {
    if (state.pyodide) return state.pyodide;
    if (state.pyodideLoading) {
        while (state.pyodideLoading) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return state.pyodide;
    }
    
    state.pyodideLoading = true;
    const statusEl = document.getElementById('pyodide-loading');
    statusEl.style.display = 'flex';
    
    try {
        console.log('Loading Pyodide...');
        state.pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
        });
        console.log('Pyodide loaded successfully');
        
        await state.pyodide.loadPackage('micropip');
        console.log('Micropip loaded');
        
        statusEl.style.display = 'none';
        state.pyodideLoading = false;
        return state.pyodide;
    } catch (err) {
        console.error('Failed to load Pyodide:', err);
        statusEl.innerHTML = '<span style="color: red;">❌ Failed to load Python. Please refresh.</span>';
        state.pyodideLoading = false;
        return null;
    }
}

// Handle file upload
function handleFileUpload(event) {
    const files = event.target.files;
    const fileList = document.getElementById('uploaded-files-list');
    
    for (let file of files) {
        // Check file size (1MB = 1048576 bytes)
        if (file.size > 1048576) {
            alert(`File ${file.name} is too large (max 1MB)`);
            continue;
        }
        
        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target.result;
            
            // Store file info
            state.uploadedFiles.push({
                name: file.name,
                content: content,
                size: file.size
            });
            
            // Update UI
            const fileItem = document.createElement('div');
            fileItem.className = 'uploaded-file-item';
            fileItem.innerHTML = `
                <span>📄 ${file.name}</span>
                <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
                <button class="remove-file-btn" onclick="window.removeUploadedFile('${file.name}')">✕</button>
            `;
            fileList.appendChild(fileItem);
            
            // Write to Pyodide filesystem if loaded
            if (state.pyodide) {
                try {
                    state.pyodide.FS.writeFile(file.name, new Uint8Array(content));
                    console.log(`File ${file.name} written to virtual filesystem`);
                } catch (err) {
                    console.error('Error writing file to filesystem:', err);
                }
            }
        };
        
        // Read as ArrayBuffer for binary support
        reader.readAsArrayBuffer(file);
    }
    
    // Reset input
    event.target.value = '';
}

// Remove uploaded file
function removeUploadedFile(filename) {
    state.uploadedFiles = state.uploadedFiles.filter(f => f.name !== filename);
    
    // Update UI
    const fileList = document.getElementById('uploaded-files-list');
    const items = fileList.querySelectorAll('.uploaded-file-item');
    items.forEach(item => {
        if (item.textContent.includes(filename)) {
            item.remove();
        }
    });
    
    // Remove from Pyodide filesystem
    if (state.pyodide) {
        try {
            state.pyodide.FS.unlink(filename);
            console.log(`File ${filename} removed from virtual filesystem`);
        } catch (err) {
            console.error('Error removing file:', err);
        }
    }
}

// Open Interactive Editor
function openEditor(pythonCode, problemTitle) {
    state.originalCode = pythonCode;
    const modal = document.getElementById('code-editor-modal');
    const editor = document.getElementById('code-editor');
    const title = document.getElementById('modal-title');
    
    title.textContent = `Interactive Editor - ${problemTitle}`;
    editor.value = pythonCode;
    modal.style.display = 'flex';
    
    // Clear previous uploads
    state.uploadedFiles = [];
    document.getElementById('uploaded-files-list').innerHTML = '';
    
    // Load Pyodide in background if not loaded
    if (!state.pyodide && !state.pyodideLoading) {
        initPyodide();
    }
}

// Close Editor
function closeEditor() {
    document.getElementById('code-editor-modal').style.display = 'none';
    document.getElementById('code-output').innerHTML = '';
    document.getElementById('test-input').value = '';
    state.uploadedFiles = [];
    document.getElementById('uploaded-files-list').innerHTML = '';
}

// Run Code
async function runCode() {
    const code = document.getElementById('code-editor').value;
    const testInput = document.getElementById('test-input').value;
    const output = document.getElementById('code-output');
    const runBtn = document.getElementById('run-code-btn');
    
    console.log('Run code clicked');
    
    output.innerHTML = '<div style="color: #888;">⏳ Running...</div>';
    runBtn.disabled = true;
    runBtn.textContent = '⏳ Running...';
    
    const pyodide = await initPyodide();
    if (!pyodide) {
        output.innerHTML = '<div style="color: red;">❌ Python environment not loaded. Please refresh the page.</div>';
        runBtn.disabled = false;
        runBtn.textContent = '▶️ Run Code';
        return;
    }
    
    console.log('Pyodide ready, executing code...');
    
    try {
        // Write uploaded files to virtual filesystem
        for (let file of state.uploadedFiles) {
            try {
                pyodide.FS.writeFile(file.name, new Uint8Array(file.content));
                console.log(`File ${file.name} available for open()`);
            } catch (err) {
                console.error(`Error writing ${file.name}:`, err);
            }
        }
        
        // Capture stdout
        let outputText = '';
        pyodide.setStdout({
            batched: (text) => {
                outputText += text;
                output.innerHTML = `<pre style="margin: 0; color: #d4d4d4;">${escapeHtml(outputText)}</pre>`;
            }
        });
        
        pyodide.setStderr({
            batched: (text) => {
                outputText += text;
                output.innerHTML = `<pre style="margin: 0; color: #ff6b6b;">${escapeHtml(outputText)}</pre>`;
            }
        });
        
        // Setup input() mock if test input provided
        if (testInput) {
            const inputLines = testInput.split('\n');
            pyodide.globals.set('__test_input_lines__', inputLines);
            
            const inputMockCode = `
import sys

__test_input_lines__ = ${JSON.stringify(inputLines)}
__test_input_index__ = [0]

def mock_input(prompt=''):
    if prompt:
        print(prompt, end='')
    if __test_input_index__[0] < len(__test_input_lines__):
        line = __test_input_lines__[__test_input_index__[0]]
        __test_input_index__[0] += 1
        print(line)
        return line
    return ''

__builtins__.input = mock_input
`;
            await pyodide.runPythonAsync(inputMockCode);
            console.log('Input mock setup complete');
        }
        
        // Run the user's code
        await pyodide.runPythonAsync(code);
        console.log('Code execution complete');
        
        if (!outputText) {
            output.innerHTML = '<div style="color: #4CAF50;">✅ Code executed successfully (no output)</div>';
        }
    } catch (err) {
        console.error('Error executing code:', err);
        output.innerHTML = `<pre style="margin: 0; color: #ff6b6b;">❌ Error:\n${escapeHtml(err.message)}</pre>`;
    }
    
    runBtn.disabled = false;
    runBtn.textContent = '▶️ Run Code';
}

// Reset Code
function resetCode() {
    document.getElementById('code-editor').value = state.originalCode;
    document.getElementById('code-output').innerHTML = '';
    document.getElementById('test-input').value = '';
}

// Download Code
function downloadCode() {
    const code = document.getElementById('code-editor').value;
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'solution.py';
    a.click();
    URL.revokeObjectURL(url);
}

// Clear Output
function clearOutput() {
    document.getElementById('code-output').innerHTML = '';
}

// Utility
function getRepoPath() {
    const parts = window.location.pathname.split('/');
    return parts[1] && parts[2] ? `${parts[1]}/${parts[2]}` : 'Vic-Nas/PythonSolutions';
}

// Load platforms from pre-generated data.json
async function loadPlatforms() {
    console.log('Loading platforms from data.json...');
    
    try {
        const res = await fetch('data.json');
        if (!res.ok) {
            console.error('Failed to load data.json');
            return;
        }
        
        const data = await res.json();
        state.platforms = data.platforms || [];
        
        state.platforms.forEach(platform => {
            state.treeData[platform.name] = platform.tree || [];
        });
        
        console.log('Loaded platforms:', state.platforms.map(p => p.name));
    } catch (err) {
        console.error('Error loading data.json:', err);
    }
}

// Find node in tree by path
function findInTree(tree, pathParts, startIndex = 0) {
    if (startIndex >= pathParts.length) return null;
    
    const currentPart = pathParts[startIndex];
    const node = tree.find(n => n.name === currentPart);
    
    if (!node) return null;
    if (startIndex === pathParts.length - 1) return node;
    if (!node.children) return null;
    
    return findInTree(node.children, pathParts, startIndex + 1);
}

// Get folder contents from tree data
function getFolderFromTree(pathParts) {
    if (pathParts.length === 0) return null;
    
    const platformName = pathParts[0];
    const tree = state.treeData[platformName];
    
    if (!tree) return null;
    if (pathParts.length === 1) return tree;
    
    const node = findInTree(tree, pathParts, 1);
    return node ? (node.children || []) : null;
}

// Check if path has files (is a problem)
function hasFiles(pathParts) {
    if (pathParts.length === 0) return false;
    
    const platformName = pathParts[0];
    const tree = state.treeData[platformName];
    
    if (!tree) return false;
    if (pathParts.length === 1) return false;
    
    const node = findInTree(tree, pathParts, 1);
    return node ? node.has_files : false;
}

// Count items in path
function countItemsFromTree(pathParts) {
    if (pathParts.length === 0) return 0;
    
    const platformName = pathParts[0];
    const tree = state.treeData[platformName];
    
    if (!tree) return 0;
    if (pathParts.length === 1) {
        return countRecursive(tree);
    }
    
    const node = findInTree(tree, pathParts, 1);
    if (!node) return 0;
    
    if (node.has_files) return 1;
    
    if (!node.children) return 0;
    return countRecursive(node.children);
    
    function countRecursive(nodes) {
        let count = 0;
        for (const n of nodes) {
            if (n.has_files) {
                count++;
            }
            if (n.children) {
                count += countRecursive(n.children);
            }
        }
        return count;
    }
}

// Fetch file contents from GitHub
async function fetchFileContent(path) {
    try {
        const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${path}`);
        if (!res.ok) return null;
        return await res.json();
    } catch (err) {
        console.error(`Error fetching ${path}:`, err);
        return null;
    }
}

// Parse hash to navigate
function parseHash() {
    let hash = window.location.hash.slice(1);
    hash = decodeURIComponent(hash);
    
    console.log('Parsing hash:', hash);
    
    if (!hash) {
        return { view: 'platforms', path: [] };
    }
    
    if (hash.startsWith('view/')) {
        const pathStr = hash.slice(5);
        const path = pathStr.split('/');
        return { view: 'problem', path };
    }
    
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
        const countText = platform.name === 'vicutils' ? 'scripts' : 'solutions';
        
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

function renderFolder() {
    const view = document.getElementById('folder-view');
    view.style.display = 'block';
    
    const items = getFolderFromTree(state.currentPath);
    
    if (!items || items.length === 0) {
        view.innerHTML = '<p>Error loading folder</p>';
        return;
    }
    
    console.log('Rendering folder:', state.currentPath, 'Items:', items);
    
    const titleParts = state.currentPath.map(capitalize);
    document.getElementById('folder-title').textContent = titleParts.join(' / ');
    
    const backBtn = document.getElementById('back-button');
    backBtn.onclick = goBack;
    
    const container = document.getElementById('folder-cards');
    container.innerHTML = '';
    
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'folder-card';
        
        const fullPath = [...state.currentPath, item.name];
        const count = countItemsFromTree(fullPath);
        
        card.innerHTML = `
            <div class="folder-card-title">${item.name}</div>
            <div class="folder-card-path">${fullPath.join('/')}</div>
            <div class="folder-card-count">${count} item${count !== 1 ? 's' : ''}</div>
        `;
        
        card.onclick = () => navigateTo(fullPath);
        container.appendChild(card);
    });
}

async function renderProblem() {
    const view = document.getElementById('problem-view');
    view.style.display = 'block';
    view.innerHTML = '<div style="text-align: center; padding: 3rem;">Loading...</div>';
    
    const pathStr = state.currentPath.join('/');
    const items = await fetchFileContent(pathStr);
    
    if (!items) {
        view.innerHTML = '<p>Error loading problem</p>';
        return;
    }
    
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
    
    if (htmlFiles.length > 0) {
        try {
            const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${pathStr}/${htmlFiles[0].name}`);
            if (res.ok) {
                const data = await res.json();
                const htmlContent = atob(data.content);
                
                const problemName = state.currentPath[state.currentPath.length - 1];
                const title = problemName.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                const subtitle = state.currentPath.slice(0, -1).map(capitalize).join(' / ');
                const githubFileUrl = `https://github.com/${getRepoPath()}/blob/main/${pathStr}/${htmlFiles[0].name}`;
                
                view.innerHTML = `
                    <div class="problem-header">
                        <div class="problem-nav">
                            <button onclick="window.goBack()" class="nav-link nav-button">← Back</button>
                            <a href="#" class="nav-link">🏠 Home</a>
                            <a href="${githubFileUrl}" target="_blank" class="nav-link">📂 GitHub File</a>
                        </div>
                        <h1 class="problem-title">${title}</h1>
                        <p class="problem-subtitle">${subtitle}</p>
                    </div>
                    <div style="width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 2rem; background: white;">
                        ${htmlContent}
                    </div>
                `;
                return;
            }
        } catch (err) {
            console.error('Error fetching HTML file:', err);
        }
    }
    
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
    
    const problemName = state.currentPath[state.currentPath.length - 1];
    const title = problemName.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const subtitle = state.currentPath.slice(0, -1).map(capitalize).join(' / ');
    
    const githubFileUrl = pyFiles.length > 0 
        ? `https://github.com/${getRepoPath()}/blob/main/${pathStr}/${pyFiles[0].name}`
        : `https://github.com/${getRepoPath()}/tree/main/${pathStr}`;
    
    const runButtonId = `run-btn-${Date.now()}`;
    let html = `
        <div class="problem-header">
            <div class="problem-nav">
                <button onclick="window.goBack()" class="nav-link nav-button">← Back</button>
                <a href="#" class="nav-link">🏠 Home</a>
                ${problemUrl ? `<a href="${problemUrl}" target="_blank" class="nav-link">🔗 Problem</a>` : ''}
                <a href="${githubFileUrl}" target="_blank" class="nav-link">📂 GitHub File</a>
                ${pythonCode ? `<button id="${runButtonId}" class="nav-link nav-button run-code-nav">▶️ Run Code</button>` : ''}
            </div>
            <h1 class="problem-title">${title}</h1>
            <p class="problem-subtitle">${subtitle}</p>
        </div>
    `;
    
    const hasSingleImage = pngFiles.length === 1;
    const hasCode = pythonCode.length > 0;
    
    if (hasSingleImage && hasCode) {
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
    
    if (pythonCode) {
        const runBtn = document.getElementById(runButtonId);
        if (runBtn) {
            runBtn.addEventListener('click', () => {
                openEditor(pythonCode, title);
            });
        }
    }
    
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }
}

// Navigation
function navigateTo(path) {
    console.log('Navigating to:', path);
    
    if (hasFiles(path)) {
        window.location.hash = `view/${path.map(encodeURIComponent).join('/')}`;
    } else {
        window.location.hash = path.map(encodeURIComponent).join('/');
    }
}

function goBack() {
    console.log('Going back from:', state.currentPath);
    
    if (state.currentView === 'problem') {
        if (state.currentPath.length > 1) {
            const parentPath = state.currentPath.slice(0, -1);
            window.location.hash = parentPath.map(encodeURIComponent).join('/');
        } else {
            window.location.hash = '';
        }
    } 
    else if (state.currentView === 'folder') {
        if (state.currentPath.length > 1) {
            const parentPath = state.currentPath.slice(0, -1);
            window.location.hash = parentPath.map(encodeURIComponent).join('/');
        } else {
            window.location.hash = '';
        }
    }
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
window.addEventListener('hashchange', () => {
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
    
    // Make functions globally available
    window.goBack = goBack;
    window.openEditor = openEditor;
    window.runCode = runCode;
    window.closeEditor = closeEditor;
    window.resetCode = resetCode;
    window.downloadCode = downloadCode;
    window.clearOutput = clearOutput;
    window.handleFileUpload = handleFileUpload;
    window.removeUploadedFile = removeUploadedFile;
    
    // Setup modal event listeners
    const modal = document.getElementById('code-editor-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'code-editor-modal') {
                closeEditor();
            }
        });
        
        document.getElementById('close-modal-btn')?.addEventListener('click', closeEditor);
        document.getElementById('run-code-btn')?.addEventListener('click', runCode);
        document.getElementById('reset-code-btn')?.addEventListener('click', resetCode);
        document.getElementById('download-code-btn')?.addEventListener('click', downloadCode);
        document.getElementById('clear-output-btn')?.addEventListener('click', clearOutput);
        document.getElementById('file-upload-input')?.addEventListener('change', handleFileUpload);
    }
    
    await loadPlatforms();
    
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPath = parsed.path;
    
    console.log('Initial state:', state);
    
    render();
})();