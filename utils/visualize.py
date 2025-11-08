# Claude AI generated code
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import webbrowser
import tempfile
import os

class AlgorithmVisualizer(ABC):
    """
    Easy-to-use template for visualizing step-by-step algorithms.
    
    Perfect for LeetCode problems! Track any variables you want (arrays, pointers, etc.)
    
    Quick Start:
    1. Inherit from this class
    2. Define your algorithm in run_algorithm() 
    3. Call self.add_step() to save each step
    4. Call .show() to see the visualization
    
    Example:
        class BinarySearch(AlgorithmVisualizer):
            def __init__(self, arr, target):
                super().__init__(
                    title="Binary Search", 
                    problem_url="https://leetcode.com/problems/binary-search/",
                    code_url="https://github.com/user/repo/blob/main/binary_search.py"
                )
                self.arr = arr
                self.target = target
            
            def run_algorithm(self):
                left, right = 0, len(self.arr) - 1
                
                while left <= right:
                    mid = (left + right) // 2
                    
                    # Save this step - visualizer handles the rest!
                    self.add_step(
                        variables={'left': left, 'right': right, 'mid': mid, 'arr': self.arr},
                        message=f"Checking middle element at index {mid}"
                    )
                    
                    if self.arr[mid] == self.target:
                        self.add_step(
                            variables={'left': left, 'right': right, 'mid': mid, 'arr': self.arr},
                            message=f"Found target {self.target} at index {mid}!",
                            highlight=[mid]
                        )
                        return mid
                    elif self.arr[mid] < self.target:
                        left = mid + 1
                    else:
                        right = mid - 1
                
                self.add_step(
                    variables={'arr': self.arr},
                    message="Target not found"
                )
                return -1
            
            def get_complexity(self):
                return {"time": "O(log n)", "space": "O(1)"}
        
        # Use it:
        BinarySearch([1,3,5,7,9], 5).show()
    """
    
    def __init__(self, title: str, description: str = "", problem_url: str = "", code_url: str = ""):
        """
        Initialize the visualizer.
        
        Args:
            title: Name of your algorithm (e.g., "Binary Search")
            description: Brief explanation (optional, will be shown as subtitle)
            problem_url: Link to the problem (e.g., LeetCode URL)
            code_url: Link to your code implementation (e.g., GitHub URL)
        """
        self.title = title
        self.description = description
        self.problem_url = problem_url
        self.code_url = code_url
        self.steps = []
        
    @abstractmethod
    def run_algorithm(self) -> Any:
        """
        🔥 IMPLEMENT THIS: Your algorithm logic goes here!
        
        Use self.add_step() to save each step you want to visualize.
        
        Example:
            def run_algorithm(self):
                arr = [3, 1, 4, 1, 5]
                for i in range(len(arr)):
                    # Save current state
                    self.add_step(
                        variables={'arr': arr, 'i': i},
                        message=f"Processing element {arr[i]} at index {i}"
                    )
                return arr
        """
        pass
    
    @abstractmethod
    def get_complexity(self) -> Dict[str, str]:
        """
        🔥 IMPLEMENT THIS: Return time/space complexity.
        
        Returns:
            Dictionary with 'time' and 'space' keys
            
        Example:
            return {
                "time": "O(n²)",
                "space": "O(1)",
                "explanation": "Nested loops for comparison"  # optional
            }
        """
        pass
    
    def add_step(self, 
                 variables: Dict[str, Any], 
                 message: str = "",
                 highlight: List[int] = None,
                 current: List[int] = None,
                 notToHighlight = []):
        """
        Save a step in your algorithm for visualization.
        
        Args:
            variables: Dict of variable names and their values
                      e.g., {'arr': [1,2,3], 'left': 0, 'right': 2}
            message: Description of what's happening this step
            highlight: List of indices to highlight (green background)
            current: List of indices to mark as "current" (blue background)
            
        Examples:
            # Simple step
            self.add_step({'arr': [1,2,3], 'i': 1}, "Checking index 1")
            
            # With highlighting
            self.add_step(
                {'arr': [1,2,3], 'left': 0, 'right': 2},
                "Found target!",
                highlight=[1]  # Highlight index 1
            )
            
            # Multiple variables
            self.add_step({
                'nums1': [1,3,5], 
                'nums2': [2,4,6],
                'i': 0, 'j': 1
            }, "Comparing nums1[0] with nums2[1]")
        """
        if highlight is None:
            highlight = []
        if current is None:
            current = []
            
        step_data = {
            'variables': variables.copy(),
            'message': message,
            'highlight': highlight,
            'current': current.copy(),
            'step_number': len(self.steps),
            "notToHighlight": notToHighlight,
        }
        self.steps.append(step_data)
    
    def show(self, auto_open: bool = True) -> str:
        """
        Generate and open the visualization in your browser.
        
        Args:
            auto_open: Whether to automatically open browser
            
        Returns:
            Path to the generated HTML file
        """
        # Run the algorithm to collect steps
        self.steps = []  # Reset steps
        try:
            result = self.run_algorithm()
            print(f"✅ Algorithm completed with {len(self.steps)} steps")
            if result is not None:
                print(f"🎯 Result: {result}")
        except Exception as e:
            print(f"❌ Error running algorithm: {e}")
            raise
        
        # Generate HTML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            html_content = self._generate_html()
            f.write(html_content)
            temp_path = f.name
        
        if auto_open:
            webbrowser.open(f'file://{os.path.abspath(temp_path)}')
            print(f"🌐 Opened visualization in browser")
        
        return temp_path
    
    def save(self, filename: str) -> str:
        """
        Save visualization to a specific file.
        
        Args:
            filename: Output HTML filename
            
        Returns:
            Path to the saved file
        """
        # Run algorithm if not done yet
        if not self.steps:
            self.run_algorithm()
        
        html_content = self._generate_html()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 Visualization saved to {filename}")
        return filename
    
    def _render_variable(self, name: str, value: Any, highlight: List[int] = None, current: List[int] = None, notToHighlight = []) -> str:
        """Convert a variable to HTML representation."""
        if highlight is None:
            highlight = []
        if current is None:
            current = []
        
        # Handle different data types
        if isinstance(value, (list, tuple)):
            return self._render_array(name, value, highlight if value not in notToHighlight else [], current)
        elif isinstance(value, dict):
            return self._render_dict(name, value)
        elif isinstance(value, (int, float, str, bool)):
            return self._render_primitive(name, value)
        else:
            return self._render_primitive(name, str(value))
    
    def _render_array(self, name: str, arr: Union[List, Tuple], highlight: List[int], current: List[int]) -> str:
        """Render an array/list with styling."""
        if not arr:
            return f'<div class="variable"><strong>{name}:</strong> []</div>'
        
        items_html = []
        for i, item in enumerate(arr):
            classes = ["array-item"]
            if i in highlight:
                classes.append("highlight")
            if i in current:
                classes.append("current")
                
            items_html.append(f'''
                <div class="{' '.join(classes)}">
                    <div class="array-index">{i}</div>
                    <div class="array-value">{item}</div>
                </div>
            ''')
        
        return f'''
            <div class="variable">
                <strong>{name}:</strong>
                <div class="array-container">
                    {''.join(items_html)}
                </div>
            </div>
        '''
    
    def _render_dict(self, name: str, d: Dict) -> str:
        """Render a dictionary."""
        items = []
        for key, val in d.items():
            items.append(f'<div class="dict-item"><span class="dict-key">{key}:</span> {val}</div>')
        
        return f'''
            <div class="variable">
                <strong>{name}:</strong>
                <div class="dict-container">
                    {''.join(items)}
                </div>
            </div>
        '''
    
    def _render_primitive(self, name: str, value: Any) -> str:
        """Render primitive values (int, float, string, etc.)."""
        return f'<div class="variable primitive"><strong>{name}:</strong> <span class="value">{value}</span></div>'
    
    def _generate_html(self) -> str:
        """Generate the complete HTML visualization."""
        complexity_info = self.get_complexity()
        
        # Convert steps to JSON
        js_steps = []
        for step in self.steps:
            # Render all variables in this step
            variables_html = []
            for var_name, var_value in step['variables'].items():
                var_html = self._render_variable(var_name, var_value, step['highlight'], step['current'], notToHighlight=step['notToHighlight'])
                variables_html.append(var_html)
            
            js_steps.append({
                'html': '\n'.join(variables_html),
                'message': step['message'],
                'step_number': step['step_number']
            })
        
        # Generate header with links
        header_html = f'<h1>🎯 {self.title}</h1>'
        
        links_html = ""
        if self.problem_url or self.code_url:
            links = []
            if self.problem_url:
                links.append(f'<a href="{self.problem_url}" target="_blank" class="header-link">📝 View Problem</a>')
            if self.code_url:
                links.append(f'<a href="{self.code_url}" target="_blank" class="header-link">💻 View Code</a>')
            links_html = f'<div class="header-links">{"".join(links)}</div>'
        
        description_html = ""
        if self.description:
            description_html = f'<p class="description">{self.description}</p>'
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <link rel="icon" href="../../VN.ico">
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {header_html}
            {links_html}
            {description_html}
        </header>

        <div class="controls">
            <button onclick="reset()">🔄 Reset</button>
            <button onclick="previousStep()" id="prevBtn">⬅️ Previous</button>
            <button onclick="nextStep()" id="nextBtn">▶️ Next</button>
            <button onclick="autoPlay()" id="autoBtn">⚡ Auto Play</button>
        </div>

        <div class="main-content">
            <div class="visualization-area">
                <div id="stateDisplay"></div>
                <div class="step-info" id="stepInfo"></div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div id="progressFill"></div>
                    </div>
                    <div class="step-counter" id="stepCounter">Step 0 of {len(js_steps)-1}</div>
                </div>
            </div>

            <div class="info-panel">
                <div class="complexity-card">
                    <h3>📊 Complexity</h3>
                    <div class="complexity-item">
                        <strong>Time:</strong> {complexity_info.get('time', 'N/A')}
                    </div>
                    <div class="complexity-item">
                        <strong>Space:</strong> {complexity_info.get('space', 'N/A')}
                    </div>
                    {f'<div class="complexity-explanation">{complexity_info.get("explanation", "")}</div>' if complexity_info.get("explanation") else ''}
                </div>
                
                <div class="shortcuts-card">
                    <h4>⌨️ Controls</h4>
                    <div class="shortcut">← → : Navigate</div>
                    <div class="shortcut">Space : Auto play</div>
                    <div class="shortcut">R : Reset</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const steps = {json.dumps(js_steps)};
        let currentStep = 0;
        let isAutoPlaying = false;

        function updateDisplay() {{
            if (steps.length === 0) return;
            
            const step = steps[currentStep];
            document.getElementById('stateDisplay').innerHTML = step.html;
            document.getElementById('stepInfo').innerHTML = step.message;
            document.getElementById('stepCounter').textContent = `Step ${{currentStep}} of ${{steps.length - 1}}`;
            
            const progress = steps.length > 1 ? (currentStep / (steps.length - 1)) * 100 : 0;
            document.getElementById('progressFill').style.width = progress + '%';
            
            document.getElementById('prevBtn').disabled = currentStep === 0;
            document.getElementById('nextBtn').disabled = currentStep === steps.length - 1;
            document.getElementById('autoBtn').disabled = currentStep === steps.length - 1;
        }}

        function nextStep() {{
            if (currentStep < steps.length - 1) {{
                currentStep++;
                updateDisplay();
            }}
        }}

        function previousStep() {{
            if (currentStep > 0) {{
                currentStep--;
                updateDisplay();
            }}
        }}

        function reset() {{
            currentStep = 0;
            isAutoPlaying = false;
            updateDisplay();
        }}

        function autoPlay() {{
            if (isAutoPlaying || currentStep === steps.length - 1) return;
            
            isAutoPlaying = true;
            const interval = setInterval(() => {{
                nextStep();
                if (currentStep === steps.length - 1) {{
                    clearInterval(interval);
                    isAutoPlaying = false;
                }}
            }}, 1500);
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextStep();
            if (e.key === 'ArrowLeft') previousStep();
            if (e.key === 'r' || e.key === 'R') reset();
            if (e.key === ' ') {{ e.preventDefault(); autoPlay(); }}
        }});

        updateDisplay();
    </script>
</body>
</html>'''
    
    def _get_css(self) -> str:
        """Generate CSS styles for the visualization."""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        header {
            text-align: center;
            margin-bottom: 32px;
        }

        h1 {
            font-size: 2.8em;
            margin-bottom: 16px;
            font-weight: 700;
            background: linear-gradient(45deg, #fff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header-links {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin: 20px 0;
            flex-wrap: wrap;
        }

        .header-link {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            color: white;
            text-decoration: none;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .header-link:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            text-decoration: none;
            color: white;
        }

        .header-link:active {
            transform: translateY(0);
        }

        .description {
            font-size: 1.2em;
            opacity: 0.9;
            max-width: 600px;
            margin: 20px auto 0;
            line-height: 1.6;
        }

        .controls {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-bottom: 32px;
            flex-wrap: wrap;
        }

        button {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 24px;
            border-radius: 16px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        button:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }

        button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }

        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 32px;
        }

        .visualization-area {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 32px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        #stateDisplay {
            min-height: 200px;
            margin-bottom: 24px;
        }

        .variable {
            margin: 20px 0;
            padding: 16px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .variable strong {
            color: #fbbf24;
            font-size: 1.1em;
            display: block;
            margin-bottom: 12px;
        }

        .array-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }

        .array-item {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 8px 12px;
            min-width: 60px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .array-item.highlight {
            background: rgba(34, 197, 94, 0.3);
            border-color: #22c55e;
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
        }

        .array-item.current {
            background: rgba(59, 130, 246, 0.3);
            border-color: #3b82f6;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        }

        .array-index {
            font-size: 0.8em;
            opacity: 0.7;
            margin-bottom: 4px;
        }

        .array-value {
            font-weight: 600;
            font-size: 1.1em;
        }

        .dict-container {
            margin-top: 8px;
        }

        .dict-item {
            padding: 4px 0;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
        }

        .dict-key {
            color: #60a5fa;
            font-weight: 600;
        }

        .primitive .value {
            color: #ffd700;
            font-weight: 600;
            font-size: 1.1em;
        }

        .step-info {
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            line-height: 1.6;
            font-size: 1.05em;
        }

        .progress-container {
            margin-top: 24px;
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
            margin-bottom: 12px;
            overflow: hidden;
        }

        #progressFill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            width: 0%;
            transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .step-counter {
            text-align: center;
            font-weight: 600;
            opacity: 0.8;
        }

        .info-panel {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .complexity-card, .shortcuts-card {
            background: rgba(255, 255, 255, 0.08);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .complexity-card h3, .shortcuts-card h4 {
            color: #4ade80;
            margin-bottom: 16px;
            font-size: 1.3em;
            font-weight: 700;
        }

        .complexity-item {
            margin: 12px 0;
            font-size: 1.05em;
        }

        .complexity-item strong {
            color: #fbbf24;
        }

        .complexity-explanation {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            font-style: italic;
            opacity: 0.9;
        }

        .shortcut {
            margin: 8px 0;
            font-family: 'SF Mono', monospace;
            background: rgba(0, 0, 0, 0.2);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 20px;
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            button {
                width: 200px;
            }
            
            .header-links {
                flex-direction: column;
                align-items: center;
            }
            
            .header-link {
                width: 200px;
                justify-content: center;
            }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fadeIn 0.4s ease-out;
        }
        '''


# Updated example implementations
class BinarySearchExample(AlgorithmVisualizer):
    """Example: Binary Search visualization"""
    
    def __init__(self, arr: List[int], target: int):
        super().__init__(
            title="Binary Search",
            description="Efficiently searching in a sorted array",
            problem_url="https://leetcode.com/problems/binary-search/",
            code_url="https://github.com/example/algorithms/blob/main/binary_search.py"
        )
        self.arr = arr
        self.target = target
    
    def run_algorithm(self) -> int:
        left, right = 0, len(self.arr) - 1
        
        self.add_step(
            {'arr': self.arr, 'left': left, 'right': right, 'target': self.target},
            f"🚀 Starting binary search for {self.target}"
        )
        
        while left <= right:
            mid = (left + right) // 2
            
            self.add_step(
                {'arr': self.arr, 'left': left, 'right': right, 'mid': mid, 'target': self.target},
                f"Checking middle element {self.arr[mid]} at index {mid}",
                current=[mid]
            )
            
            if self.arr[mid] == self.target:
                self.add_step(
                    {'arr': self.arr, 'left': left, 'right': right, 'mid': mid, 'target': self.target},
                    f"🎯 Found {self.target} at index {mid}!",
                    highlight=[mid]
                )
                return mid
            elif self.arr[mid] < self.target:
                self.add_step(
                    {'arr': self.arr, 'left': left, 'right': right, 'mid': mid, 'target': self.target},
                    f"{self.arr[mid]} < {self.target}, search right half"
                )
                left = mid + 1
            else:
                self.add_step(
                    {'arr': self.arr, 'left': left, 'right': right, 'mid': mid, 'target': self.target},
                    f"{self.arr[mid]} > {self.target}, search left half"
                )
                right = mid - 1
        
        self.add_step(
            {'arr': self.arr, 'target': self.target},
            f"❌ Target {self.target} not found"
        )
        return -1
    
    def get_complexity(self) -> Dict[str, str]:
        return {
            "time": "O(log n)",
            "space": "O(1)",
            "explanation": "Each step eliminates half the search space"
        }


if __name__ == "__main__":
    print("🎨 Enhanced Algorithm Visualizer with Links")
    print("=" * 50)
    print("\n✨ Quick Examples:")
    print("\n📚 Check the docstrings for full usage guide!")
    
    # Example usage
    # visualizer = BinarySearchExample([1, 3, 5, 7, 9, 11, 13], 7)
    # visualizer.show()