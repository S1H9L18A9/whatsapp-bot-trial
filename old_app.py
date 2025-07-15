from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import random
import uuid

app = FastAPI()

# Data models
class FunctionIO(BaseModel):
    name: str
    type: str
    
class FunctionBox(BaseModel):
    id: str
    name: str
    description: str
    inputs: List[FunctionIO]
    outputs: List[FunctionIO]
    x: float = 100
    y: float = 100

class Connection(BaseModel):
    id: str
    source_box: str
    source_output: str
    target_box: str
    target_input: str

class GraphData(BaseModel):
    boxes: List[FunctionBox]
    connections: List[Connection]

# Global storage (in production, use a database)
current_graph = GraphData(boxes=[], connections=[])

# Sample function definitions
SAMPLE_FUNCTIONS = [
    {
        "name": "add_numbers",
        "description": "Adds two integers together",
        "inputs": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "outputs": [{"name": "result", "type": "int"}]
    },
    {
        "name": "multiply_numbers", 
        "description": "Multiplies two integers",
        "inputs": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "outputs": [{"name": "result", "type": "int"}]
    },
    {
        "name": "to_string",
        "description": "Converts an integer to string",
        "inputs": [{"name": "value", "type": "int"}],
        "outputs": [{"name": "text", "type": "str"}]
    },
    {
        "name": "get_length",
        "description": "Gets the length of a string",
        "inputs": [{"name": "text", "type": "str"}],
        "outputs": [{"name": "length", "type": "int"}]
    },
    {
        "name": "concatenate",
        "description": "Joins two strings together",
        "inputs": [{"name": "a", "type": "str"}, {"name": "b", "type": "str"}],
        "outputs": [{"name": "result", "type": "str"}]
    },
    {
        "name": "uppercase",
        "description": "Converts string to uppercase",
        "inputs": [{"name": "text", "type": "str"}],
        "outputs": [{"name": "upper_text", "type": "str"}]
    },
    {
        "name": "generate_random",
        "description": "Generates a random integer",
        "inputs": [],
        "outputs": [{"name": "number", "type": "int"}]
    },
    {
        "name": "format_message",
        "description": "Formats a message with a number",
        "inputs": [{"name": "template", "type": "str"}, {"name": "value", "type": "int"}],
        "outputs": [{"name": "message", "type": "str"}]
    }
]

@app.post("/chat")
async def chat(message: dict):
    """Mock chat endpoint that generates function boxes based on user input"""
    user_message = message.get("message", "")
    
    # Simple keyword matching for demo
    keywords = {
        "add": ["add_numbers", "multiply_numbers"],
        "string": ["to_string", "concatenate", "uppercase"],
        "length": ["get_length"],
        "random": ["generate_random"],
        "format": ["format_message"]
    }
    
    # Find matching functions
    matching_functions = []
    for keyword, functions in keywords.items():
        if keyword in user_message.lower():
            matching_functions.extend(functions)
    
    # If no matches, return a random function
    if not matching_functions:
        matching_functions = [random.choice(SAMPLE_FUNCTIONS)["name"]]
    
    # Create function boxes
    new_boxes = []
    for func_name in matching_functions[:2]:  # Limit to 2 boxes per request
        func_def = next(f for f in SAMPLE_FUNCTIONS if f["name"] == func_name)
        
        box = FunctionBox(
            id=str(uuid.uuid4()),
            name=func_def["name"],
            description=func_def["description"],
            inputs=[FunctionIO(**inp) for inp in func_def["inputs"]],
            outputs=[FunctionIO(**out) for out in func_def["outputs"]],
            x=random.randint(100, 500),
            y=random.randint(100, 300)
        )
        new_boxes.append(box)
        current_graph.boxes.append(box)
    
    return {
        "response": f"I found {len(new_boxes)} function(s) that might help: {', '.join([b.name for b in new_boxes])}",
        "boxes": [box.dict() for box in new_boxes]
    }

@app.get("/boxes")
async def get_boxes():
    """Get all current function boxes"""
    return [box.dict() for box in current_graph.boxes]

@app.post("/boxes/{box_id}/position")
async def update_box_position(box_id: str, position: dict):
    """Update a box's position"""
    box = next((b for b in current_graph.boxes if b.id == box_id), None)
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    
    box.x = position["x"]
    box.y = position["y"]
    return {"status": "updated"}

@app.post("/connections")
async def create_connection(connection: dict):
    """Create a new connection between boxes"""
    # Validate connection types
    source_box = next((b for b in current_graph.boxes if b.id == connection["source_box"]), None)
    target_box = next((b for b in current_graph.boxes if b.id == connection["target_box"]), None)
    
    if not source_box or not target_box:
        raise HTTPException(status_code=404, detail="Box not found")
    
    # Find output and input types
    source_output = next((o for o in source_box.outputs if o.name == connection["source_output"]), None)
    target_input = next((i for i in target_box.inputs if i.name == connection["target_input"]), None)
    
    if not source_output or not target_input:
        raise HTTPException(status_code=404, detail="Input/Output not found")
    
    # Validate types match
    if source_output.type != target_input.type:
        raise HTTPException(status_code=400, detail=f"Type mismatch: {source_output.type} -> {target_input.type}")
    
    # Create connection
    conn = Connection(
        id=str(uuid.uuid4()),
        **connection
    )
    current_graph.connections.append(conn)
    
    return conn.dict()

@app.get("/connections")
async def get_connections():
    """Get all connections"""
    return [conn.dict() for conn in current_graph.connections]

@app.delete("/connections/{connection_id}")
async def delete_connection(connection_id: str):
    """Delete a connection"""
    current_graph.connections = [c for c in current_graph.connections if c.id != connection_id]
    return {"status": "deleted"}

@app.get("/export")
async def export_graph():
    """Export the current graph as JSON"""
    return {
        "boxes": [box.dict() for box in current_graph.boxes],
        "connections": [conn.dict() for conn in current_graph.connections]
    }

@app.delete("/clear")
async def clear_graph():
    """Clear all boxes and connections"""
    current_graph.boxes.clear()
    current_graph.connections.clear()
    return {"status": "cleared"}

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serve the frontend HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visual Function Composer</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
                color: #ffffff;
                height: 100vh;
                overflow: hidden;
            }
            
            .container {
                display: flex;
                height: 100vh;
                flex-direction: column;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .header h1 {
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .header-actions {
                display: flex;
                gap: 1rem;
            }
            
            .btn {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .workspace {
                flex: 1;
                position: relative;
                overflow: hidden;
                background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
            }
            
            .function-box {
                position: absolute;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 1rem;
                min-width: 200px;
                cursor: move;
                transition: all 0.3s ease;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                overflow: visible;
            }
            
            .function-box:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
                border-color: rgba(255, 255, 255, 0.3);
            }
            
            .function-box.dragging {
                transform: scale(1.05);
                z-index: 1000;
            }
            
            .function-title {
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #4fc3f7;
            }
            
            .function-description {
                font-size: 0.8rem;
                color: #b0b0b0;
                margin-bottom: 1rem;
            }
            
            .io-section {
                margin-bottom: 0.5rem;
            }
            
            .io-label {
                font-size: 0.7rem;
                color: #888;
                margin-bottom: 0.3rem;
                text-transform: uppercase;
                font-weight: 500;
            }
            
            .io-item {
                display: flex;
                align-items: center;
                margin-bottom: 0.3rem;
                padding: 0.3rem 0.5rem;
                border-radius: 6px;
                background: rgba(255, 255, 255, 0.05);
                position: relative;
                margin-left: 10px;
                margin-right: 10px;
            }
            
            .io-name {
                flex: 1;
                font-size: 0.8rem;
            }
            
            .io-type {
                font-size: 0.7rem;
                color: #4fc3f7;
                font-weight: 500;
            }
            
            .io-connector {
                width: 14px;
                height: 14px;
                border-radius: 50%;
                border: 2px solid;
                position: absolute;
                cursor: crosshair;
                transition: all 0.3s ease;
                z-index: 10;
                top: 50%;
                transform: translateY(-50%);
            }
            
            .input-connector {
                left: -17px;
                background: #1e1e2e;
                border-color: #4fc3f7;
            }
            
            .output-connector {
                right: -17px;
                background: #1e1e2e;
                border-color: #81c784;
            }
            
            .io-connector:hover {
                transform: translateY(-50%) scale(1.3);
                box-shadow: 0 0 10px currentColor;
            }
            
            .chat-panel {
                height: 200px;
                background: rgba(0, 0, 0, 0.3);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                flex-direction: column;
            }
            
            .chat-messages {
                flex: 1;
                padding: 1rem;
                overflow-y: auto;
            }
            
            .chat-input-area {
                padding: 1rem;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                gap: 1rem;
            }
            
            .chat-input {
                flex: 1;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 0.7rem;
                color: white;
                font-size: 0.9rem;
            }
            
            .chat-input::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            
            .chat-input:focus {
                outline: none;
                border-color: #4fc3f7;
            }
            
            .message {
                margin-bottom: 1rem;
                padding: 0.7rem;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
            }
            
            .message.user {
                background: rgba(76, 175, 80, 0.2);
                text-align: right;
            }
            
            .message.assistant {
                background: rgba(33, 150, 243, 0.2);
            }
            
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
            
            .connection-path {
                fill: none;
                stroke: #4fc3f7;
                stroke-width: 2;
                filter: drop-shadow(0 0 4px rgba(79, 195, 247, 0.5));
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Visual Function Composer</h1>
                <div class="header-actions">
                    <button class="btn" onclick="exportGraph()">Export</button>
                    <button class="btn" onclick="clearGraph()">Clear</button>
                </div>
            </div>
            
            <div class="main-content">
                <div class="workspace" id="workspace">
                    <svg class="connection-svg" id="connectionSvg"></svg>
                </div>
                
                <div class="chat-panel">
                    <div class="chat-messages" id="chatMessages">
                        <div class="message assistant">
                            Welcome! Ask me to create functions and I'll generate them for you. Try asking for "add numbers" or "string functions".
                        </div>
                    </div>
                    <div class="chat-input-area">
                        <input type="text" class="chat-input" id="chatInput" placeholder="Ask for functions..." />
                        <button class="btn" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let boxes = [];
            let connections = [];
            let draggedBox = null;
            let dragOffset = { x: 0, y: 0 };
            let connectionStart = null;
            let tempConnection = null;
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                loadBoxes();
                loadConnections();
                setupEventListeners();
            });
            
            function setupEventListeners() {
                const chatInput = document.getElementById('chatInput');
                chatInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
                
                const workspace = document.getElementById('workspace');
                workspace.addEventListener('mousemove', handleMouseMove);
                workspace.addEventListener('mouseup', handleMouseUp);
            }
            
            async function sendMessage() {
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage(message, 'user');
                input.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message })
                    });
                    const data = await response.json();
                    
                    // Add assistant response
                    addMessage(data.response, 'assistant');
                    
                    // Add new boxes
                    if (data.boxes) {
                        data.boxes.forEach(box => {
                            boxes.push(box);
                            renderBox(box);
                        });
                    }
                } catch (error) {
                    addMessage('Sorry, there was an error processing your request.', 'assistant');
                }
            }
            
            function addMessage(text, sender) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                messageDiv.textContent = text;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            async function loadBoxes() {
                try {
                    const response = await fetch('/boxes');
                    boxes = await response.json();
                    boxes.forEach(renderBox);
                } catch (error) {
                    console.error('Error loading boxes:', error);
                }
            }
            
            async function loadConnections() {
                try {
                    const response = await fetch('/connections');
                    connections = await response.json();
                    renderConnections();
                } catch (error) {
                    console.error('Error loading connections:', error);
                }
            }
            
            function renderBox(box) {
                const boxElement = document.createElement('div');
                boxElement.className = 'function-box';
                boxElement.style.left = box.x + 'px';
                boxElement.style.top = box.y + 'px';
                boxElement.id = 'box-' + box.id;
                
                let inputsHtml = '';
                if (box.inputs && box.inputs.length > 0) {
                    inputsHtml = `
                        <div class="io-section">
                            <div class="io-label">Inputs</div>
                            ${box.inputs.map(input => `
                                <div class="io-item">
                                    <div class="input-connector" data-box="${box.id}" data-input="${input.name}" data-type="${input.type}"></div>
                                    <span class="io-name">${input.name}</span>
                                    <span class="io-type">${input.type}</span>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
                
                let outputsHtml = '';
                if (box.outputs && box.outputs.length > 0) {
                    outputsHtml = `
                        <div class="io-section">
                            <div class="io-label">Outputs</div>
                            ${box.outputs.map(output => `
                                <div class="io-item">
                                    <span class="io-name">${output.name}</span>
                                    <span class="io-type">${output.type}</span>
                                    <div class="output-connector" data-box="${box.id}" data-output="${output.name}" data-type="${output.type}"></div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
                
                boxElement.innerHTML = `
                    <div class="function-title">${box.name}</div>
                    <div class="function-description">${box.description}</div>
                    ${inputsHtml}
                    ${outputsHtml}
                `;
                
                // Add drag functionality - but not for connectors
                boxElement.addEventListener('mousedown', function(e) {
                    // Don't drag if clicking on a connector
                    if (e.target.classList.contains('input-connector') || e.target.classList.contains('output-connector')) {
                        return;
                    }
                    
                    draggedBox = box;
                    const rect = boxElement.getBoundingClientRect();
                    const workspaceRect = document.getElementById('workspace').getBoundingClientRect();
                    dragOffset.x = e.clientX - rect.left;
                    dragOffset.y = e.clientY - rect.top;
                    boxElement.classList.add('dragging');
                    e.preventDefault();
                });
                
                // Add connector event listeners with better event handling
                boxElement.querySelectorAll('.output-connector').forEach(connector => {
                    connector.addEventListener('mousedown', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        console.log('Starting connection from:', this.dataset.box, this.dataset.output);
                        connectionStart = {
                            box: this.dataset.box,
                            output: this.dataset.output,
                            type: this.dataset.type,
                            element: this
                        };
                        this.style.background = '#81c784';
                    });
                });
                
                boxElement.querySelectorAll('.input-connector').forEach(connector => {
                    connector.addEventListener('mouseenter', function(e) {
                        if (connectionStart) {
                            if (connectionStart.type === this.dataset.type) {
                                this.style.background = '#4fc3f7';
                                this.style.borderColor = '#4fc3f7';
                            } else {
                                this.style.background = '#f44336';
                                this.style.borderColor = '#f44336';
                            }
                        }
                    });
                    
                    connector.addEventListener('mouseleave', function(e) {
                        this.style.background = '#1e1e2e';
                        this.style.borderColor = '#4fc3f7';
                    });
                    
                    connector.addEventListener('mouseup', function(e) {
                        e.stopPropagation();
                        console.log('Ending connection at:', this.dataset.box, this.dataset.input);
                        if (connectionStart) {
                            createConnection(connectionStart, {
                                box: this.dataset.box,
                                input: this.dataset.input,
                                type: this.dataset.type,
                                element: this
                            });
                            
                            // Reset all connector styles
                            document.querySelectorAll('.output-connector').forEach(c => {
                                c.style.background = '#1e1e2e';
                            });
                        }
                    });
                });
                
                document.getElementById('workspace').appendChild(boxElement);
            }
            
            function handleMouseMove(e) {
                if (draggedBox) {
                    const workspaceRect = document.getElementById('workspace').getBoundingClientRect();
                    const newX = e.clientX - workspaceRect.left - dragOffset.x;
                    const newY = e.clientY - workspaceRect.top - dragOffset.y;
                    
                    const boxElement = document.getElementById('box-' + draggedBox.id);
                    boxElement.style.left = newX + 'px';
                    boxElement.style.top = newY + 'px';
                    
                    draggedBox.x = newX;
                    draggedBox.y = newY;
                    
                    renderConnections();
                }
            }
            
            function handleMouseUp(e) {
                if (draggedBox) {
                    const boxElement = document.getElementById('box-' + draggedBox.id);
                    boxElement.classList.remove('dragging');
                    
                    // Update position on server
                    fetch(`/boxes/${draggedBox.id}/position`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ x: draggedBox.x, y: draggedBox.y })
                    });
                    
                    draggedBox = null;
                }
                
                connectionStart = null;
            }
            
            async function createConnection(start, end) {
                if (start.type !== end.type) {
                    addMessage(`Cannot connect ${start.type} to ${end.type}`, 'assistant');
                    return;
                }
                
                try {
                    const response = await fetch('/connections', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            source_box: start.box,
                            source_output: start.output,
                            target_box: end.box,
                            target_input: end.input
                        })
                    });
                    
                    if (response.ok) {
                        const connection = await response.json();
                        connections.push(connection);
                        renderConnections();
                    } else {
                        const error = await response.json();
                        addMessage(`Connection failed: ${error.detail}`, 'assistant');
                    }
                } catch (error) {
                    addMessage('Error creating connection', 'assistant');
                }
            }
            
            function renderConnections() {
                const svg = document.getElementById('connectionSvg');
                svg.innerHTML = '';
                
                connections.forEach(connection => {
                    const sourceBox = document.getElementById('box-' + connection.source_box);
                    const targetBox = document.getElementById('box-' + connection.target_box);
                    
                    if (!sourceBox || !targetBox) return;
                    
                    const sourceConnector = sourceBox.querySelector(`[data-output="${connection.source_output}"]`);
                    const targetConnector = targetBox.querySelector(`[data-input="${connection.target_input}"]`);
                    
                    if (!sourceConnector || !targetConnector) return;
                    
                    const sourceRect = sourceConnector.getBoundingClientRect();
                    const targetRect = targetConnector.getBoundingClientRect();
                    const workspaceRect = document.getElementById('workspace').getBoundingClientRect();
                    
                    const startX = sourceRect.left - workspaceRect.left + sourceRect.width / 2;
                    const startY = sourceRect.top - workspaceRect.top + sourceRect.height / 2;
                    const endX = targetRect.left - workspaceRect.left + targetRect.width / 2;
                    const endY = targetRect.top - workspaceRect.top + targetRect.height / 2;
                    
                    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    const midX = (startX + endX) / 2;
                    const d = `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`;
                    path.setAttribute('d', d);
                    path.setAttribute('class', 'connection-path');
                    
                    svg.appendChild(path);
                });
            }
            
            async function exportGraph() {
                try {
                    const response = await fetch('/export');
                    const data = await response.json();
                    
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'function_graph.json';
                    a.click();
                    URL.revokeObjectURL(url);
                } catch (error) {
                    addMessage('Error exporting graph', 'assistant');
                }
            }
            
            async function clearGraph() {
                if (confirm('Are you sure you want to clear all boxes and connections?')) {
                    try {
                        await fetch('/clear', { method: 'DELETE' });
                        boxes = [];
                        connections = [];
                        document.getElementById('workspace').innerHTML = '<svg class="connection-svg" id="connectionSvg"></svg>';
                        addMessage('Graph cleared', 'assistant');
                    } catch (error) {
                        addMessage('Error clearing graph', 'assistant');
                    }
                }
            }
            
            // Handle window resize
            window.addEventListener('resize', function() {
                setTimeout(renderConnections, 100);
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)