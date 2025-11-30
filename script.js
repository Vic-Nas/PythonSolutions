// State
const state = {
    data: { leetcode: [], kattis: [], vicutils: [] },
    currentView: 'loading',
    currentPlatform: null,
    currentProblem: null
};

// Utility
function getRepoPath() {
    const parts = window.location.pathname.split('/');
    return parts[1] && parts[2] ? `${parts[1]}/${parts[2]}` : 'Vic-Nas/PythonSolutions';
}

// Fetch repository data
async function fetchRepoData() {
    const platforms = ['leetcode', 'kattis', 'vicutils'];
    
    for (const platform of platforms) {
        try {
            const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${platform}`);
            if (!res.ok) continue;
            
            const items = await res.json();
            const problems = [];
            
            if (platform === 'vicutils') {
                // VicUtils: scan for HTML files only
                for (const item of items) {
                    if (item.type === 'file' && item.name.endsWith('.html')) {
                        problems.push({
                            name: item.name.replace('.html', ''),
                            fullName: item.name,
                            type: 'html',
                            files: { html: [item], png: [], py: [] }
                        });
                    }
                }
            } else {
                // LeetCode/Kattis: scan directories
                const dirs = items.filter(i => i.type === 'dir');
                
                for (const dir of dirs) {
                    const dirRes = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${platform}/${dir.name}`);
                    if (!dirRes.ok) continue;
                    
                    const files = await dirRes.json();
                    
                    const htmlFiles = files.filter(f => f.name.endsWith('.html'));
                    const pngFiles = files.filter(f => f.name.endsWith('.vn.png') || f.name.match(/\.vn\.\d+\.png$/))
                        .sort((a, b) => {
                            const numA = a.name.match(/\.(\d+)\.png$/)?.[1] || 0;
                            const numB = b.name.match(/\.(\d+)\.png$/)?.[1] || 0;
                            return parseInt(numA) - parseInt(numB);
                        });
                    const pyFiles = files.filter(f => f.name.endsWith('.vn.py') && !f.name.includes('.shortest.'));
                    
                    if (htmlFiles.length || pngFiles.length || pyFiles.length) {
                        let type = 'code';
                        if (htmlFiles.length) type = 'html';
                        else if (pngFiles.length) type = 'png';
                        
                        problems.push({
                            name: dir.name,
                            type,
                            files: { html: htmlFiles, png: pngFiles, py: pyFiles }
                        });
                    }
                }
            }
            
            state.data[platform] = problems.sort((a, b) => a.name.localeCompare(b.name));
        } catch (err) {
            console.error(`Error loading ${platform}:`, err);
        }
    }
}

// Render views
function render() {
    const views = ['loading-screen', 'platform-selector', 'problem-list', 'problem-view'];
    views.forEach(v => document.getElementById(v).style.display = 'none');
    
    if (state.currentView === 'loading') {
        document.getElementById('loading-screen').style.display = 'flex';
    } else if (state.currentView === 'platforms') {
        renderPlatforms();
    } else if (state.currentView === 'list') {
        renderProblemList();
    } else if (state.currentView === 'problem') {
        renderProblemView();
    }
}

function renderPlatforms() {
    document.getElementById('platform-selector').style.display = 'block';
    document.getElementById('leetcode-count').textContent = `${state.data.leetcode.length} problems`;
    document.getElementById('kattis-count').textContent = `${state.data.kattis.length} problems`;
    document.getElementById('vicutils-count').textContent = `${state.data.vicutils.length} scripts`;
}

function renderProblemList() {
    const listView = document.getElementById('problem-list');
    listView.style.display = 'block';
    
    const platform = state.currentPlatform;
    const problems = state.data[platform];
    
    document.getElementById('list-title').textContent = 
        platform === 'vicutils' ? 'VicUtils Scripts' : `${capitalize(platform)} Problems`;
    
    const container = document.getElementById('problem-cards');
    container.innerHTML = '';
    
    problems.forEach(prob => {
        const card = document.createElement('div');
        card.className = 'problem-card';
        
        const badge = prob.type === 'html' ? 'badge-html' : 
                     prob.type === 'png' ? 'badge-png' : 'badge-code';
        const badgeText = prob.type === 'html' ? 'HTML' : 
                         prob.type === 'png' ? 'IMAGE' : 'CODE';
        
        card.innerHTML = `
            <div class="problem-card-title">${prob.name}</div>
            <div class="problem-card-path">${platform}/${prob.name}</div>
            <span class="problem-type-badge ${badge}">${badgeText}</span>
        `;
        
        card.onclick = () => navigateToProblem(platform, prob);
        container.appendChild(card);
    });
}

async function renderProblemView() {
    const view = document.getElementById('problem-view');
    view.style.display = 'block';
    view.innerHTML = '<div style="text-align: center; padding: 3rem;">Loading...</div>';
    
    const platform = state.currentPlatform;
    const problem = state.currentProblem;
    
    // Fetch Python code if available
    let pythonCode = '';
    let problemUrl = '';
    
    if (problem.files.py.length > 0) {
        try {
            const pyFile = problem.files.py[0];
            const path = platform === 'vicutils' ? `${platform}/${pyFile.name}` : `${platform}/${problem.name}/${pyFile.name}`;
            const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${path}`);
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
    const title = problem.name.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const subtitle = platform === 'vicutils' ? 'Utility Script' : `${capitalize(platform)} Solution`;
    
    const repoUrl = platform === 'vicutils' 
        ? `https://github.com/${getRepoPath()}/blob/main/${platform}/${problem.fullName || problem.name}`
        : `https://github.com/${getRepoPath()}/tree/main/${platform}/${problem.name}`;
    
    let html = `
        <div class="problem-header">
            <div class="problem-nav">
                <a href="javascript:history.back()" class="nav-link">← Back</a>
                <a href="${window.location.pathname}" class="nav-link">🏠 Home</a>
                ${problemUrl ? `<a href="${problemUrl}" target="_blank" class="nav-link">🔗 Problem</a>` : ''}
                <a href="${repoUrl}" target="_blank" class="nav-link">📂 GitHub</a>
            </div>
            <h1 class="problem-title">${title}</h1>
            <p class="problem-subtitle">${subtitle}</p>
        </div>
    `;
    
    const hasSingleImage = problem.files.png.length === 1;
    const hasCode = pythonCode.length > 0;
    
    if (hasSingleImage && hasCode) {
        // Side-by-side layout
        html += '<div class="content-wrapper">';
        
        // Image side
        html += '<div class="visual-panel">';
        const imgUrl = `${platform}/${problem.name}/${problem.files.png[0].name}`;
        html += `
            <div class="image-box">
                <img src="${imgUrl}" alt="Solution">
                <div class="image-label">Solution Visualization</div>
            </div>
        `;
        html += '</div>';
        
        // Code side
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
        
        if (problem.files.png.length > 0) {
            if (problem.files.png.length === 1) {
                const imgUrl = `${platform}/${problem.name}/${problem.files.png[0].name}`;
                html += `
                    <div class="image-box">
                        <img src="${imgUrl}" alt="Solution">
                        <div class="image-label">Solution Visualization</div>
                    </div>
                `;
            } else {
                html += '<div class="multi-image-grid">';
                problem.files.png.forEach((img, i) => {
                    const imgUrl = `${platform}/${problem.name}/${img.name}`;
                    html += `
                        <div class="image-box">
                            <img src="${imgUrl}" alt="Step ${i + 1}">
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
function navigateToPlatform(platform) {
    state.currentView = 'list';
    state.currentPlatform = platform;
    window.location.hash = platform;
    render();
}

function navigateToProblem(platform, problem) {
    // Check if has HTML page
    if (problem.files.html.length > 0) {
        const htmlFile = problem.files.html[0].name;
        window.location.href = platform === 'vicutils' 
            ? `${platform}/${problem.fullName}`
            : `${platform}/${problem.name}/${htmlFile}`;
        return;
    }
    
    state.currentView = 'problem';
    state.currentPlatform = platform;
    state.currentProblem = problem;
    const encodedName = encodeURIComponent(problem.name);
    window.location.hash = `view/${platform}/${encodedName}`;
    render();
}

function navigateToHome() {
    state.currentView = 'platforms';
    state.currentPlatform = null;
    state.currentProblem = null;
    window.location.hash = '';
    render();
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

// Event listeners
document.addEventListener('click', e => {
    if (e.target.classList.contains('platform-box') || e.target.closest('.platform-box')) {
        const box = e.target.closest('.platform-box') || e.target;
        const platform = box.dataset.platform;
        if (platform) navigateToPlatform(platform);
    }
});

document.getElementById('back-to-platforms')?.addEventListener('click', navigateToHome);

window.addEventListener('hashchange', () => {
    const hash = window.location.hash.slice(1);
    
    if (!hash) {
        navigateToHome();
    } else if (hash.startsWith('view/')) {
        // Remove 'view/' prefix first
        const remainder = hash.substring(5);
        // Split only on the first slash to separate platform from problem name
        const firstSlashIndex = remainder.indexOf('/');
        if (firstSlashIndex === -1) {
            navigateToHome();
        } else {
            const platform = remainder.substring(0, firstSlashIndex);
            const problemName = decodeURIComponent(remainder.substring(firstSlashIndex + 1));
            console.log('hashchange - Looking for problem:', problemName, 'in platform:', platform);
            const problem = state.data[platform]?.find(p => p.name === problemName);
            if (problem) {
                state.currentView = 'problem';
                state.currentPlatform = platform;
                state.currentProblem = problem;
                render();
            } else {
                // Problem not found, go to platform list
                state.currentView = 'list';
                state.currentPlatform = platform;
                render();
            }
        }
    } else if (['leetcode', 'kattis', 'vicutils'].includes(hash)) {
        navigateToPlatform(hash);
    }
});

// Initialize
(async () => {
    // Check if we're on index.html or root path
    const isIndexPage = window.location.pathname.endsWith('index.html') || 
                        window.location.pathname.endsWith('/') || 
                        window.location.pathname.split('/').pop() === '';
    
    if (!isIndexPage) {
        // We're on a direct problem HTML page - don't initialize the SPA
        return;
    }
    
    await fetchRepoData();
    
    const hash = window.location.hash.slice(1);
    
    if (hash.startsWith('view/')) {
        // Remove 'view/' prefix first
        const remainder = hash.substring(5);
        // Split only on the first slash to separate platform from problem name
        const firstSlashIndex = remainder.indexOf('/');
        if (firstSlashIndex === -1) {
            state.currentView = 'platforms';
        } else {
            const platform = remainder.substring(0, firstSlashIndex);
            const problemName = decodeURIComponent(remainder.substring(firstSlashIndex + 1));
            console.log('Looking for problem:', problemName, 'in platform:', platform);
            console.log('Available problems:', state.data[platform]?.map(p => p.name));
            const problem = state.data[platform]?.find(p => p.name === problemName);
            if (problem) {
                state.currentView = 'problem';
                state.currentPlatform = platform;
                state.currentProblem = problem;
            } else {
                console.warn('Problem not found:', problemName);
                state.currentView = 'platforms';
            }
        }
    } else if (['leetcode', 'kattis', 'vicutils'].includes(hash)) {
        state.currentView = 'list';
        state.currentPlatform = hash;
    } else {
        state.currentView = 'platforms';
    }
    
    render();
})();