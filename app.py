from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import random
import uvicorn

app = FastAPI()

# Sample function templates
FUNCTION_TEMPLATES = [
    {
        "name": "add_numbers",
        "inputs": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "outputs": [{"name": "result", "type": "int"}],
        "description": "Add two integers"
    },
    {
        "name": "to_string", 
        "inputs": [{"name": "value", "type": "int"}],
        "outputs": [{"name": "text", "type": "str"}],
        "description": "Convert integer to string"
    },
    {
        "name": "get_length",
        "inputs": [{"name": "text", "type": "str"}],
        "outputs": [{"name": "length", "type": "int"}],
        "description": "Get string length"
    },
    {
        "name": "concatenate",
        "inputs": [{"name": "a", "type": "str"}, {"name": "b", "type": "str"}],
        "outputs": [{"name": "result", "type": "str"}],
        "description": "Concatenate two strings"
    },
    {
        "name": "multiply",
        "inputs": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "outputs": [{"name": "result", "type": "int"}],
        "description": "Multiply two integers"
    },
    {
        "name": "split_string",
        "inputs": [{"name": "text", "type": "str"}, {"name": "delimiter", "type": "str"}],
        "outputs": [{"name": "parts", "type": "list"}],
        "description": "Split string by delimiter"
    },
    {
        "name": "filter_positive",
        "inputs": [{"name": "numbers", "type": "list"}],
        "outputs": [{"name": "positive", "type": "list"}],
        "description": "Filter positive numbers"
    },
    {
        "name": "format_text",
        "inputs": [{"name": "template", "type": "str"}, {"name": "value", "type": "int"}],
        "outputs": [{"name": "formatted", "type": "str"}],
        "description": "Format text with value"
    }
]

@app.get("/", response_class=HTMLResponse)
async def get_app():
    return HTML_CONTENT

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    
    # Generate 2-3 random functions based on the message
    num_functions = random.randint(2, 3)
    selected_functions = random.sample(FUNCTION_TEMPLATES, num_functions)
    
    return {
        "functions": selected_functions,
        "response": f"Here are some functions for '{message}'"
    }

@app.post("/api/export")
async def export_graph(request: Request):
    data = await request.json()
    # In a real app, you'd save this to a database
    return {"status": "exported", "graph": data}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Function Composer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: #fff;
            overflow: hidden;
            height: 100vh;
        }

        .app-container {
            display: grid;
            grid-template-columns: 320px 1fr;
            height: 100vh;
        }

        .sidebar {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            overflow-y: auto;
        }

        .sidebar h2 {
            margin-bottom: 20px;
            font-size: 1.2em;
            color: #64ffda;
            text-align: center;
        }

        .chat-container {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chat-input {
            width: 100%;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            color: #fff;
            margin-bottom: 10px;
        }

        .chat-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        .chat-btn {
            background: linear-gradient(45deg, #64ffda, #1de9b6);
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            color: #000;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
        }

        .chat-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(100, 255, 218, 0.4);
        }

        .functions-list {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-height: 400px;
            overflow-y: auto;
        }

        .function-template {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }

        .function-template:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }

        .function-name {
            font-weight: bold;
            color: #64ffda;
            margin-bottom: 5px;
            cursor: grab;
            padding: 5px;
            border-radius: 3px;
            transition: background 0.2s ease;
        }

        .function-name:hover {
            background: rgba(100, 255, 218, 0.1);
        }

        .function-name:active {
            cursor: grabbing;
        }

        .function-signature {
            font-size: 0.85em;
            color: #ccc;
            font-family: 'Courier New', monospace;
            margin-bottom: 5px;
        }

        .function-description {
            font-size: 0.8em;
            color: #aaa;
            font-style: italic;
        }

        .canvas-container {
            position: relative;
            background: rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .canvas {
            width: 100%;
            height: 100%;
            position: relative;
        }

        .function-box {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            min-width: 250px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            user-select: none;
        }

        .function-box-content {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
        }

        .function-box-header {
            font-weight: bold;
            color: #64ffda;
            margin-bottom: 10px;
            cursor: grab;
            padding: 5px;
            border-radius: 3px;
            transition: background 0.2s ease;
        }

        .function-box-header:hover {
            background: rgba(100, 255, 218, 0.1);
        }

        .function-box-header:active {
            cursor: grabbing;
        }

        .inputs, .outputs {
            flex: 1;
        }

        .inputs {
            text-align: left;
        }

        .outputs {
            text-align: right;
        }

        .inputs h4, .outputs h4 {
            font-size: 0.9em;
            color: #ccc;
            margin-bottom: 5px;
        }

        .connector {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            font-size: 0.85em;
        }

        .input-connector {
            justify-content: flex-start;
        }

        .output-connector {
            justify-content: flex-end;
        }

        .output-connector .connector-dot {
            order: 2;
            margin-left: 8px;
            margin-right: 0;
        }

        .connector-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid;
            margin-right: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .input-connector .connector-dot {
            border-color: #ff6b6b;
            background: rgba(255, 107, 107, 0.2);
        }

        .output-connector .connector-dot {
            border-color: #4ecdc4;
            background: rgba(78, 205, 196, 0.2);
        }

        .connector-dot:hover {
            transform: scale(1.2);
            box-shadow: 0 0 10px currentColor;
        }

        .type-int { color: #61dafb; }
        .type-str { color: #98fb98; }
        .type-list { color: #dda0dd; }
        .type-float { color: #f0e68c; }

        .connection-line {
            position: absolute;
            pointer-events: none;
            z-index: 1;
        }

        .connection-svg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .export-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            color: #fff;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
        }

        .export-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .drag-preview {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            pointer-events: none;
            z-index: 1000;
            opacity: 0.8;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leader-line/1.0.7/leader-line.min.js"></script>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <h2>🔧 Function Composer</h2>
            
            <div class="chat-container">
                <input type="text" class="chat-input" placeholder="Ask for functions..." id="chatInput">
                <button class="chat-btn" onclick="sendChat()">Generate Functions</button>
            </div>

            <div class="functions-list" id="functionsList">
                <h3 style="color: #64ffda; margin-bottom: 10px;">Available Functions</h3>
                <div id="functionsContainer"></div>
            </div>

            <button class="export-btn" onclick="exportGraph()">Export Graph</button>
        </div>

        <div class="canvas-container">
            
            <div class="canvas" id="canvas"></div>
        </div>
    </div>

    <script>
        let nextBoxId = 1;
        let boxes = [];
        let connections = [];
        let leaderLines = [];
        let draggedElement = null;
        let dragOffset = { x: 0, y: 0 };
        let isDragging = false;
        let dragPreview = null;

        // Type colors
        const typeColors = {
            'int': '#61dafb',
            'str': '#98fb98', 
            'list': '#dda0dd',
            'float': '#f0e68c'
        };

        // Initialize with some default functions
        window.onload = function() {
            loadDefaultFunctions();
        };

        async function loadDefaultFunctions() {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: 'basic functions' })
                });
                const data = await response.json();
                displayFunctions(data.functions);
            } catch (error) {
                console.error('Error loading functions:', error);
            }
        }

        async function sendChat() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                displayFunctions(data.functions);
                input.value = '';
            } catch (error) {
                console.error('Error sending chat:', error);
            }
        }

        function displayFunctions(functions) {
            const container = document.getElementById('functionsContainer');
            container.innerHTML = '';
            
            functions.forEach(func => {
                const div = document.createElement('div');
                div.className = 'function-template';
                div.innerHTML = `
                    <div class="function-name" data-function='${JSON.stringify(func)}'>${func.name}</div>
                    <div class="function-signature">
                        (${func.inputs.map(i => `${i.name}: ${i.type}`).join(', ')}) → ${func.outputs.map(o => o.type).join(', ')}
                    </div>
                    <div class="function-description">${func.description}</div>
                `;
                container.appendChild(div);
            });

            // Add drag handlers to function names
            container.querySelectorAll('.function-name').forEach(nameEl => {
                nameEl.addEventListener('mousedown', startDragFromSidebar);
            });
        }

        function startDragFromSidebar(e) {
            e.preventDefault();
            isDragging = true;
            
            const funcData = JSON.parse(e.target.dataset.function);
            const rect = e.target.getBoundingClientRect();
            
            dragOffset.x = e.clientX - rect.left;
            dragOffset.y = e.clientY - rect.top;
            
            // Create drag preview
            dragPreview = document.createElement('div');
            dragPreview.className = 'drag-preview';
            dragPreview.innerHTML = createFunctionBoxContent(funcData);
            dragPreview.style.left = (e.clientX - dragOffset.x) + 'px';
            dragPreview.style.top = (e.clientY - dragOffset.y) + 'px';
            document.body.appendChild(dragPreview);
            
            draggedElement = { type: 'new', data: funcData };
            
            document.addEventListener('mousemove', handleDragMove);
            document.addEventListener('mouseup', handleDragEnd);
        }

        function handleDragMove(e) {
            if (!isDragging || !draggedElement) return;
            
            if (dragPreview) {
                dragPreview.style.left = (e.clientX - dragOffset.x) + 'px';
                dragPreview.style.top = (e.clientY - dragOffset.y) + 'px';
            }
            
            if (draggedElement.type === 'existing') {
                const box = document.getElementById(draggedElement.id);
                if (box) {
                    const canvasRect = document.getElementById('canvas').getBoundingClientRect();
                    box.style.left = (e.clientX - canvasRect.left - dragOffset.x) + 'px';
                    box.style.top = (e.clientY - canvasRect.top - dragOffset.y) + 'px';
                    updateConnections();
                }
            }
        }

        function handleDragEnd(e) {
            if (!isDragging) return;
            
            isDragging = false;
            
            if (dragPreview) {
                dragPreview.remove();
                dragPreview = null;
            }
            
            if (draggedElement && draggedElement.type === 'new') {
                const canvasRect = document.getElementById('canvas').getBoundingClientRect();
                const x = e.clientX - canvasRect.left - dragOffset.x;
                const y = e.clientY - canvasRect.top - dragOffset.y;
                
                if (x >= 0 && y >= 0 && x < canvasRect.width && y < canvasRect.height) {
                    createFunctionBox(draggedElement.data, x, y);
                }
            }
            
            draggedElement = null;
            document.removeEventListener('mousemove', handleDragMove);
            document.removeEventListener('mouseup', handleDragEnd);
            // Update leader lines after drag
setTimeout(() => {
    updateConnections();
}, 50);
        }

        function createFunctionBox(funcData, x, y) {
            const boxId = 'box-' + nextBoxId++;
            const box = document.createElement('div');
            box.className = 'function-box';
            box.id = boxId;
            box.style.left = x + 'px';
            box.style.top = y + 'px';
            box.innerHTML = createFunctionBoxContent(funcData);
            
            // Add drag handler to header only
            const header = box.querySelector('.function-box-header');
            header.addEventListener('mousedown', (e) => startDragBox(e, boxId));
            
            document.getElementById('canvas').appendChild(box);
            
            boxes.push({
                id: boxId,
                data: funcData,
                x: x,
                y: y
            });
            
            // Add connector event handlers
            addConnectorHandlers(box);
        }

        function createFunctionBoxContent(funcData) {
            return `
                <div class="function-box-header">${funcData.name}</div>
                <div class="function-box-content">
                    <div class="inputs">
                        <h4>Inputs</h4>
                        ${funcData.inputs.map((input, i) => `
                            <div class="connector input-connector">
                                <div class="connector-dot" data-type="${input.type}" data-direction="input" data-index="${i}"></div>
                                <span class="type-${input.type}">${input.name}: ${input.type}</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="outputs">
                        <h4>Outputs</h4>
                        ${funcData.outputs.map((output, i) => `
                            <div class="connector output-connector">
                                <span class="type-${output.type}">${output.name}: ${output.type}</span>
                                <div class="connector-dot" data-type="${output.type}" data-direction="output" data-index="${i}"></div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        function startDragBox(e, boxId) {
            e.preventDefault();
            e.stopPropagation();
            
            isDragging = true;
            const box = document.getElementById(boxId);
            const rect = box.getBoundingClientRect();
            const canvasRect = document.getElementById('canvas').getBoundingClientRect();
            
            dragOffset.x = e.clientX - rect.left;
            dragOffset.y = e.clientY - rect.top;
            
            draggedElement = { type: 'existing', id: boxId };
            
            document.addEventListener('mousemove', handleDragMove);
            document.addEventListener('mouseup', handleDragEnd);
        }

        function addConnectorHandlers(box) {
            const connectors = box.querySelectorAll('.connector-dot');
            connectors.forEach(connector => {
                connector.addEventListener('click', handleConnectorClick);
            });
        }

        let selectedConnector = null;

        function handleConnectorClick(e) {
            e.stopPropagation();
            
            const connector = e.target;
            const boxId = connector.closest('.function-box').id;
            const direction = connector.dataset.direction;
            const type = connector.dataset.type;
            const index = connector.dataset.index;
            
            if (!selectedConnector) {
                // First connector selected
                selectedConnector = { boxId, direction, type, index, element: connector };
                connector.style.boxShadow = '0 0 15px currentColor';
            } else {
                // Second connector selected - try to create connection
                const canConnect = 
                    selectedConnector.direction !== direction && 
                    selectedConnector.type === type &&
                    selectedConnector.boxId !== boxId;
                
                if (canConnect) {
                    createConnection(selectedConnector, { boxId, direction, type, index, element: connector });
                }
                
                // Reset selection
                selectedConnector.element.style.boxShadow = '';
                selectedConnector = null;
            }
        }

        
        function createConnection(from, to) {
    const fromBox = document.getElementById(from.boxId);
    const toBox = document.getElementById(to.boxId);
    
    const fromConnector = fromBox.querySelector(`[data-direction="output"][data-index="${from.index}"]`);
    const toConnector = toBox.querySelector(`[data-direction="input"][data-index="${to.index}"]`);
    
    if (!fromConnector || !toConnector) return;
    
    const line = new LeaderLine(fromConnector, toConnector, {
        color: typeColors[from.type] || '#64ffda',
        size: 3,
        path: 'fluid',
        startSocket: 'right',
        endSocket: 'left',
        gradient: true,
        dropShadow: true
    });
    
    const connection = {
        id: 'conn-' + Date.now(),
        from: from,
        to: to,
        line: line
    };
    
    connections.push(connection);
    leaderLines.push(line);
}

        function updateConnections() {
    // Leader Line automatically updates positions
    leaderLines.forEach(line => {
        if (line && line.position) {
            line.position();
        }
    });
}

        function exportGraph() {
            const graphData = {
                boxes: boxes.map(box => ({
                    id: box.id,
                    function: box.data,
                    position: { x: box.x, y: box.y }
                })),
                connections: connections
            };
            
            fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(graphData)
            }).then(() => {
                alert('Graph exported successfully!');
                console.log('Exported graph:', graphData);
            });
        }

        // Handle Enter key in chat input
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChat();
            }
        });

        // Update connections when window resizes
        window.addEventListener('resize', updateConnections);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)