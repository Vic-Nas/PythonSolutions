let problemsData = {
    leetcode: [],
    kattis: [],
    vicutils: []
};

const main =  document.getElementById("main")


async function scanForProblems() {
    const platforms = ['leetcode', 'kattis', 'vicutils'];
    
    for (const platform of platforms) {
        try {
            const response = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${platform}`);
            
            if (!response.ok) {
                console.warn(`Could not access ${platform} directory`);
                continue;
            }
            
            const items = await response.json();
            const problems = [];
            
            if (platform === 'vicutils') {
                // For vicutils, look for generated .html files
                for (const item of items) {
                    if (item.type === 'file' && item.name.endsWith('.html')) {
                        problems.push({
                            name: item.name,  // Keep the full filename
                            displayName: item.name.replace('.html', '').replace(/_/g, ' '),
                            type: 'html',
                            hasPage: true,
                            hasHtml: true,
                            hasPng: false,
                            hasPy: false,
                            mainPyFile: null,
                            htmlFiles: [item],
                            pngFiles: [],
                            pyFiles: []
                        });
                    }
                }
            } else {
                // For leetcode and kattis, process directories
                const directories = items.filter(item => item.type === 'dir');
                
                for (const dir of directories) {
                    try {
                        const dirResponse = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${platform}/${dir.name}`);
                        if (dirResponse.ok) {
                            const files = await dirResponse.json();
                            
                            const hasHtml = files.some(file => 
                                file.name.endsWith('.html') && 
                                file.name.toLowerCase().includes(dir.name.toLowerCase().replace(/\s+/g, ''))
                            );
                            
                            const pngFiles = files.filter(file => 
                                file.name.endsWith('.vn.png') || 
                                file.name.match(/\.vn\.\d+\.png$/)
                            );
                            const hasPng = pngFiles.length > 0;
                            
                            const pyFiles = files.filter(file => file.name.endsWith('.vn.py'));
                            const hasPy = pyFiles.length > 0;
                            
                            let type = 'code-only';
                            let hasPage = false;
                            let mainPyFile = null;
                            
                            if (hasHtml) {
                                type = 'html';
                                hasPage = true;
                            } else if (hasPng) {
                                type = 'png';
                                hasPage = true;
                            } else if (hasPy) {
                                type = 'code-only';
                                hasPage = true;
                            }
                            
                            if (pyFiles.length > 0) {
                                mainPyFile = pyFiles[0];
                            }
                            
                            if (hasHtml || hasPng || hasPy) {
                                problems.push({
                                    name: dir.name,
                                    displayName: dir.name,
                                    type: type,
                                    hasPage: hasPage,
                                    hasHtml: hasHtml,
                                    hasPng: hasPng,
                                    hasPy: hasPy,
                                    mainPyFile: mainPyFile,
                                    htmlFiles: files.filter(file => file.name.endsWith('.html')),
                                    pngFiles: pngFiles.sort((a, b) => {
                                        const aNum = a.name.match(/\.(\d+)\.png$/) ? parseInt(a.name.match(/\.(\d+)\.png$/)[1]) : 0;
                                        const bNum = b.name.match(/\.(\d+)\.png$/) ? parseInt(b.name.match(/\.(\d+)\.png$/)[1]) : 0;
                                        return aNum - bNum;
                                    }),
                                    pyFiles: pyFiles
                                });
                            }
                        }
                    } catch (error) {
                        console.warn(`Could not scan directory ${dir.name}:`, error);
                    }
                }
            }
            
            problemsData[platform] = problems.sort((a, b) => a.name.localeCompare(b.name));
        } catch (error) {
            console.error(`Error scanning ${platform}:`, error);
        }
    }
    
    updateUI();
}

function getRepoPath() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts[1] && pathParts[2]) {
        return `${pathParts[1]}/${pathParts[2]}`;
    }
    return 'Vic-Nas/PythonSolutions';
}

function updateUI() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('main-view').style.display = 'grid';
    
    for (const platform of ['leetcode', 'kattis', 'vicutils']) {
        const problems = problemsData[platform];
        const totalProblems = problems.length;
        const label = platform === 'vicutils' ? 'scripts' : 'problems';
        
        document.getElementById(`${platform}-count`).textContent = `${totalProblems} ${label}`;
    }
}

function showProblems(platform) {
    const problems = problemsData[platform];
    const title = platform === 'vicutils' ? 'VicUtils' : platform.charAt(0).toUpperCase() + platform.slice(1);
    
    document.getElementById('main-view').style.display = 'none';
    document.getElementById('problems-view').style.display = 'block';
    document.getElementById('problems-title').textContent = platform === 'vicutils' ? 'Utility Scripts' : `${title} Problems`;
    
    const container = document.getElementById('problems-container');
    
    if (problems.length === 0) {
        container.innerHTML = '<div class="no-problems">No items found for this section yet.</div>';
        return;
    }
    
    const grid = document.createElement('div');
    grid.className = 'problems-grid';
    
    problems.forEach(problem => {
        const item = document.createElement('div');
        item.className = `problem-item ${problem.type}-page`;
        
        let icon = '';
        if (problem.type === 'html') icon = '🌐';
        else if (problem.type === 'png') icon = '🖼️';
        else if (problem.type === 'util-script') icon = '🛠️';
        else icon = '💻';
        
        const displayPath = platform === 'vicutils' ? problem.name : `${platform}/${problem.name}`;
        
        item.innerHTML = `
            <div class="problem-name">
                <span class="problem-type-icon">${icon}</span>
                ${problem.displayName}
            </div>
            <div class="problem-path">${displayPath}</div>
        `;
        
        if (platform === 'vicutils') {
            // For vicutils, link directly to the HTML file
            item.onclick = () => window.location.href = `${platform}/${problem.name}`;
        } else if (problem.hasHtml && problem.htmlFiles.length > 0) {
            // For leetcode and kattis, maintain the subfolder structure
            item.onclick = () => window.location.href = `${platform}/${problem.name}/${problem.htmlFiles[0].name}`;
        } else {
            item.onclick = () => generatePage(platform, problem);
        }
        
        grid.appendChild(item);
    });
    
    container.innerHTML = '';
    container.appendChild(grid);
}

function showMainView() {
    document.getElementById('problems-view').style.display = 'none';
    document.getElementById('main-view').style.display = 'grid';
}

async function generatePage(platform, problem) {
    const problemId = encodeURIComponent(`${platform}/${problem.name}`);
    const newUrl = `${window.location.origin}${window.location.pathname}#view/${problemId}`;
    window.location.href = newUrl;
}

async function renderProblemPage(platform, problemName) {
    const problem = problemsData[platform]?.find(p => p.name === problemName);
    if (!problem) {
        main.innerHTML = '<div class="error">Item not found</div>';
        return;
    }
    
    let problemUrl = '';
    let pythonCode = '';
    
    if (problem.hasPy && problem.mainPyFile) {
        try {
            const pyResponse = await fetch(`https://api.github.com/repos/${getRepoPath()}/contents/${platform === 'vicutils' ? platform : `${platform}/${problem.name}`}/${problem.mainPyFile.name}`);
            if (pyResponse.ok) {
                const pyData = await pyResponse.json();
                const content = atob(pyData.content);
                pythonCode = content;
                
                const urlMatch = content.match(/^#.*?(https:\/\/[^\s]+)/m);
                if (urlMatch) {
                    problemUrl = urlMatch[1];
                }
            }
        } catch (error) {
            console.warn('Could not fetch Python file:', error);
        }
    }
    
    const pageTitle = problem.displayName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const platformTitle = platform === 'vicutils' ? 'VicUtils' : platform.charAt(0).toUpperCase() + platform.slice(1);
    
    const repoUrl = platform === 'vicutils' 
        ? `https://github.com/${getRepoPath()}/blob/main/${platform}/${problem.name}`
        : `https://github.com/${getRepoPath()}/tree/main/${platform}/${problem.name}`;
    
    let pageContent = `
        <div class="generated-page">
            <div class="nav-buttons">
                <a href="javascript:history.back()" class="nav-btn">← Back</a>
                <a href="${window.location.pathname}" class="nav-btn">🏠 Home</a>
                ${problemUrl ? `<a href="${problemUrl}" target="_blank" class="nav-btn">🔗 Problem</a>` : ''}
                <a href="${repoUrl}" target="_blank" class="nav-btn">
                    <img src="VN.ico" alt="GitHub" style="width: 16px; height: 16px; margin-right: 4px;">
                    Code
                </a>
            </div>
            
            <h1 class="page-title">${pageTitle}</h1>
            <p class="page-subtitle">${platformTitle}${platform === 'vicutils' ? ' Script' : ' Problem Solution'}</p>
    `;
    
    if (problem.hasPng && problem.pngFiles.length > 0) {
        pageContent += `<div class="images-grid">`;
        
        problem.pngFiles.forEach((pngFile, index) => {
            const imageUrl = `${platform}/${problem.name}/${pngFile.name}`;
            const caption = problem.pngFiles.length > 1 ? `Solution Step ${index + 1}` : 'Solution Visualization';
            
            pageContent += `
                <div class="image-container">
                    <img src="${imageUrl}" alt="${caption}" loading="lazy">
                    <div class="image-caption">${caption}</div>
                </div>
            `;
        });
        
        pageContent += `</div>`;
    }
    
    if (pythonCode) {
        pageContent += `
            <div class="code-section">
                <h3>Python ${platform === 'vicutils' ? 'Script' : 'Solution'}</h3>
                <div class="code-content"><pre>${escapeHtml(pythonCode)}</pre></div>
            </div>
        `;
    }
    
    pageContent += `</div>`;
    
    main.innerHTML = pageContent;
    document.title = `${pageTitle} - ${platformTitle}`;
    
    if (!document.querySelector('link[rel="icon"]')) {
        const link = document.createElement('link');
        link.rel = 'icon';
        link.href = 'VN.ico';
        document.head.appendChild(link);
    }
}

function escapeHtml(text) {
    const code = document.createElement('code');
    code.classList.add("language-python")
    code.textContent = text;
    return code.outerHTML;
}

function addNavigationToCurrentPage() {
    const path = window.location.pathname;
    const isLeetCodeProblem = path.includes('/leetcode/') && path.endsWith('.html');
    const isKattisProblem = path.includes('/kattis/') && path.endsWith('.html');
    
    if (isLeetCodeProblem || isKattisProblem) {
        const platform = isLeetCodeProblem ? 'leetcode' : 'kattis';
        const backButton = document.createElement('div');
        backButton.innerHTML = `
            <style>
                .nav-buttons {
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    z-index: 1000;
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                }
                .nav-btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 0.75rem 1rem;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    font-weight: 500;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                }
                .nav-btn:hover {
                    background: #5a6fd8;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                }
                @media (max-width: 768px) {
                    .nav-buttons {
                        position: relative;
                        top: 0;
                        left: 0;
                        margin-bottom: 1rem;
                        justify-content: center;
                    }
                }
            </style>
            <div class="nav-buttons">
                <a href="../../index.html" class="nav-btn">← Home</a>
                <a href="../../index.html#${platform}" class="nav-btn">${platform.charAt(0).toUpperCase() + platform.slice(1)} Problems</a>
            </div>
        `;
        main.insertBefore(backButton, document.body.firstChild);
    }
}

// Initialize the app
if (window.location.pathname.endsWith('index.html') || 
    window.location.pathname.endsWith('/') || 
    window.location.pathname.split('/').pop() === '') {
    
    // Handle hash navigation for problem views
    const hash = window.location.hash;
    if (hash.startsWith('#view/')) {
        const problemPath = decodeURIComponent(hash.substring(6));
        const [platform, problemName] = problemPath.split('/');
        
        // Load problems data first, then render the problem page
        scanForProblems().then(() => {
            renderProblemPage(platform, problemName);
        });
    } else {
        scanForProblems();
        
        // Handle platform navigation
        window.addEventListener('load', () => {
            const simpleHash = window.location.hash.substring(1);
            if (simpleHash === 'leetcode' || simpleHash === 'kattis' || simpleHash === 'vicutils') {
                setTimeout(() => showProblems(simpleHash), 1000);
            }
        });
    }
} else {
    addNavigationToCurrentPage();
}

// Handle browser back/forward navigation
window.addEventListener('hashchange', () => {
    const hash = window.location.hash;
    if (hash.startsWith('#view/')) {
        const problemPath = decodeURIComponent(hash.substring(6));
        const [platform, problemName] = problemPath.split('/');
        renderProblemPage(platform, problemName);
    } else if (hash === '') {
        location.reload(); // Reload to show main page
    }
});


window.onload = () => {
    hljs.highlightAll();
}