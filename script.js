console.log('Script loaded');

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
    console.log('Fetching repo data...');
    const platforms = ['leetcode', 'kattis', 'vicutils'];
    
    for (const platform of platforms) {
        try {
            const res = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${platform}`);
            if (!res.ok) continue;
            
            const items = await res.json();
            const problems = [];
            
            if (platform === 'vicutils') {
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
            console.log(`Loaded ${problems.length} items for ${platform}`);
        } catch (err) {
            console.error(`Error loading ${platform}:`, err);
        }
    }
}

// Parse hash to get view state
function parseHash() {
    const hash = window.location.hash.slice(1);
    console.log('Parsing hash:', hash);
    
    if (!hash) {
        return { view: 'platforms', platform: null, problem: null };
    }
    
    if (hash.startsWith('view/')) {
        const remainder = hash.slice(5); // Remove 'view/'
        const slashIndex = remainder.indexOf('/');
        
        if (slashIndex === -1) {
            return { view: 'platforms', platform: null, problem: null };
        }
        
        const platform = remainder.slice(0, slashIndex);
        const problemName = decodeURIComponent(remainder.slice(slashIndex + 1));
        
        console.log('Parsed view - platform:', platform, 'problem:', problemName);
        
        const problem = state.data[platform]?.find(p => p.name === problemName);
        
        if (problem) {
            console.log('Found problem:', problem);
            return { view: 'problem', platform, problem };
        } else {
            console.warn('Problem not found. Available:', state.data[platform]?.map(p => p.name));
            return { view: 'list', platform, problem: null };
        }
    }
    
    if (['leetcode', 'kattis', 'vicutils'].includes(hash)) {
        return { view: 'list', platform: hash, problem: null };
    }
    
    return { view: 'platforms', platform: null, problem: null };
}

// Render views
function render() {
    console.log('Rendering view:', state.currentView);
    
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
    
    console.log('Rendering problem:', problem.name, 'from platform:', platform);
    
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
                <a href="#${platform}" class="nav-link">← Back</a>
                <a href="#" class="nav-link">🏠 Home</a>
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
    console.log('Navigating to platform:', platform);
    window.location.hash = platform;
}

function navigateToProblem(platform, problem) {
    console.log('Navigating to problem:', problem.name);
    
    // Check if has HTML page
    if (problem.files.html.length > 0) {
        const htmlFile = problem.files.html[0].name;
        window.location.href = platform === 'vicutils' 
            ? `${platform}/${problem.fullName}`
            : `${platform}/${problem.name}/${htmlFile}`;
        return;
    }
    
    const encodedName = encodeURIComponent(problem.name);
    window.location.hash = `view/${platform}/${encodedName}`;
}

function navigateToHome() {
    console.log('Navigating to home');
    window.location.hash = '';
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
    console.log('Hash changed');
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPlatform = parsed.platform;
    state.currentProblem = parsed.problem;
    render();
});

// Initialize
(async () => {
    console.log('Initializing app...');
    
    // Check if we're on index page
    const isIndexPage = window.location.pathname.endsWith('index.html') || 
                        window.location.pathname.endsWith('/') || 
                        window.location.pathname.split('/').pop() === '';
    
    console.log('Is index page:', isIndexPage);
    
    if (!isIndexPage) {
        console.log('Not index page, skipping initialization');
        return;
    }
    
    await fetchRepoData();
    
    const parsed = parseHash();
    state.currentView = parsed.view;
    state.currentPlatform = parsed.platform;
    state.currentProblem = parsed.problem;
    
    console.log('Initial state:', state);
    
    render();
})();