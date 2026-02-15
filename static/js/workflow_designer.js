/**
 * Visual Workflow Designer
 * Canvas-based drag-and-drop workflow and reflex rule designer
 * Inspired by beak-lims visual rule design
 */

const WorkflowDesigner = (function() {
    'use strict';

    // Configuration
    let config = {
        canvasId: 'workflowCanvas',
        containerId: 'canvasContainer',
        gridSize: 20,
        nodeWidth: 160,
        nodeHeight: 60,
        zoomMin: 0.25,
        zoomMax: 2.0,
        zoomStep: 0.1
    };

    // State
    let state = {
        nodes: [],
        connections: [],
        selectedNode: null,
        selectedConnection: null,
        draggingNode: null,
        connectingFrom: null,
        zoom: 1,
        panX: 0,
        panY: 0,
        undoStack: [],
        redoStack: [],
        isDirty: false
    };

    // DOM Elements
    let canvas, container, nodesLayer, connectionsLayer;

    // Node Types Configuration
    const nodeTypes = {
        start: { color: '#4CAF50', shape: 'circle', label: 'Start' },
        end: { color: '#f44336', shape: 'circle', label: 'End' },
        step: { color: '#2196F3', shape: 'rect', label: 'Process' },
        decision: { color: '#FF9800', shape: 'diamond', label: 'Decision' },
        receive: { color: '#9C27B0', shape: 'rect', label: 'Receive' },
        extract: { color: '#00BCD4', shape: 'rect', label: 'Extract' },
        amplify: { color: '#E91E63', shape: 'rect', label: 'Amplify' },
        sequence: { color: '#3F51B5', shape: 'rect', label: 'Sequence' },
        analyze: { color: '#009688', shape: 'rect', label: 'Analyze' },
        report: { color: '#795548', shape: 'rect', label: 'Report' },
        condition: { color: '#FF5722', shape: 'diamond', label: 'Condition' },
        trigger: { color: '#673AB7', shape: 'rect', label: 'Trigger' },
        notification: { color: '#FFC107', shape: 'rect', label: 'Notify' },
        qc_check: { color: '#8BC34A', shape: 'rect', label: 'QC Check' },
        approval: { color: '#CDDC39', shape: 'rect', label: 'Approval' }
    };

    // Initialize the designer
    function init(options) {
        Object.assign(config, options);

        canvas = document.getElementById(config.canvasId);
        container = document.getElementById(config.containerId);
        nodesLayer = document.getElementById('nodesLayer');
        connectionsLayer = document.getElementById('connectionsLayer');

        setupEventListeners();
        setupDragAndDrop();
        updateCanvasSize();

        console.log('Workflow Designer initialized');
    }

    // Setup event listeners
    function setupEventListeners() {
        // Canvas events
        canvas.addEventListener('click', handleCanvasClick);
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseup', handleMouseUp);

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyDown);

        // Window resize
        window.addEventListener('resize', updateCanvasSize);

        // Properties panel updates
        document.getElementById('propertiesContent').addEventListener('change', handlePropertyChange);
    }

    // Setup drag and drop from palette
    function setupDragAndDrop() {
        const paletteItems = document.querySelectorAll('.palette-item');

        paletteItems.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('nodeType', item.dataset.nodeType);
            });
        });

        container.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        container.addEventListener('drop', (e) => {
            e.preventDefault();
            const nodeType = e.dataTransfer.getData('nodeType');
            if (nodeType) {
                const rect = container.getBoundingClientRect();
                const x = (e.clientX - rect.left - state.panX) / state.zoom;
                const y = (e.clientY - rect.top - state.panY) / state.zoom;
                addNode(nodeType, snapToGrid(x), snapToGrid(y));
            }
        });
    }

    // Add a new node
    function addNode(type, x, y) {
        const nodeConfig = nodeTypes[type];
        if (!nodeConfig) return null;

        const node = {
            id: generateId(),
            type: type,
            x: x,
            y: y,
            width: config.nodeWidth,
            height: config.nodeHeight,
            label: nodeConfig.label,
            properties: getDefaultProperties(type)
        };

        saveState();
        state.nodes.push(node);
        renderNode(node);
        selectNode(node);
        state.isDirty = true;

        return node;
    }

    // Render a node on the canvas
    function renderNode(node) {
        const nodeConfig = nodeTypes[node.type];
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('id', `node-${node.id}`);
        group.setAttribute('class', 'workflow-node');
        group.setAttribute('transform', `translate(${node.x}, ${node.y})`);
        group.dataset.nodeId = node.id;

        let shape;
        if (nodeConfig.shape === 'circle') {
            shape = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            shape.setAttribute('cx', node.width / 2);
            shape.setAttribute('cy', node.height / 2);
            shape.setAttribute('r', Math.min(node.width, node.height) / 2 - 5);
        } else if (nodeConfig.shape === 'diamond') {
            shape = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            const cx = node.width / 2, cy = node.height / 2;
            const hw = node.width / 2 - 5, hh = node.height / 2 - 5;
            shape.setAttribute('points', `${cx},${cy-hh} ${cx+hw},${cy} ${cx},${cy+hh} ${cx-hw},${cy}`);
        } else {
            shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            shape.setAttribute('x', 5);
            shape.setAttribute('y', 5);
            shape.setAttribute('width', node.width - 10);
            shape.setAttribute('height', node.height - 10);
            shape.setAttribute('rx', 5);
        }

        shape.setAttribute('fill', nodeConfig.color);
        shape.setAttribute('stroke', '#333');
        shape.setAttribute('stroke-width', '2');
        shape.setAttribute('class', 'node-shape');

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.width / 2);
        text.setAttribute('y', node.height / 2 + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#fff');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.label;

        // Connection points
        const ports = createPorts(node);

        group.appendChild(shape);
        group.appendChild(text);
        ports.forEach(port => group.appendChild(port));

        // Event listeners
        group.addEventListener('mousedown', (e) => handleNodeMouseDown(e, node));
        group.addEventListener('dblclick', (e) => handleNodeDoubleClick(e, node));

        nodesLayer.appendChild(group);
    }

    // Create connection ports for a node
    function createPorts(node) {
        const ports = [];
        const positions = [
            { x: node.width / 2, y: 0, type: 'input' },
            { x: node.width / 2, y: node.height, type: 'output' },
            { x: 0, y: node.height / 2, type: 'input' },
            { x: node.width, y: node.height / 2, type: 'output' }
        ];

        positions.forEach((pos, i) => {
            const port = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            port.setAttribute('cx', pos.x);
            port.setAttribute('cy', pos.y);
            port.setAttribute('r', 6);
            port.setAttribute('fill', pos.type === 'input' ? '#4CAF50' : '#2196F3');
            port.setAttribute('stroke', '#fff');
            port.setAttribute('stroke-width', '2');
            port.setAttribute('class', `port port-${pos.type}`);
            port.dataset.portIndex = i;
            port.dataset.portType = pos.type;

            port.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                if (pos.type === 'output') {
                    startConnection(node, i);
                }
            });

            port.addEventListener('mouseup', (e) => {
                e.stopPropagation();
                if (pos.type === 'input' && state.connectingFrom) {
                    completeConnection(node, i);
                }
            });

            ports.push(port);
        });

        return ports;
    }

    // Start creating a connection
    function startConnection(fromNode, portIndex) {
        state.connectingFrom = { node: fromNode, port: portIndex };
        canvas.style.cursor = 'crosshair';
    }

    // Complete a connection
    function completeConnection(toNode, portIndex) {
        if (!state.connectingFrom) return;
        if (state.connectingFrom.node.id === toNode.id) {
            state.connectingFrom = null;
            canvas.style.cursor = 'default';
            return;
        }

        saveState();

        const connection = {
            id: generateId(),
            from: { nodeId: state.connectingFrom.node.id, port: state.connectingFrom.port },
            to: { nodeId: toNode.id, port: portIndex },
            label: ''
        };

        state.connections.push(connection);
        renderConnection(connection);
        state.connectingFrom = null;
        canvas.style.cursor = 'default';
        state.isDirty = true;
    }

    // Render a connection
    function renderConnection(conn) {
        const fromNode = state.nodes.find(n => n.id === conn.from.nodeId);
        const toNode = state.nodes.find(n => n.id === conn.to.nodeId);
        if (!fromNode || !toNode) return;

        const fromPort = getPortPosition(fromNode, conn.from.port);
        const toPort = getPortPosition(toNode, conn.to.port);

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const d = calculatePath(fromPort, toPort);
        path.setAttribute('d', d);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', '#666');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('marker-end', 'url(#arrowhead)');
        path.setAttribute('class', 'connection');
        path.setAttribute('id', `conn-${conn.id}`);
        path.dataset.connectionId = conn.id;

        path.addEventListener('click', (e) => {
            e.stopPropagation();
            selectConnection(conn);
        });

        connectionsLayer.appendChild(path);
    }

    // Calculate curved path between ports
    function calculatePath(from, to) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const cx = from.x + dx / 2;

        return `M ${from.x} ${from.y} C ${cx} ${from.y}, ${cx} ${to.y}, ${to.x} ${to.y}`;
    }

    // Get port position in canvas coordinates
    function getPortPosition(node, portIndex) {
        const positions = [
            { x: node.x + node.width / 2, y: node.y },
            { x: node.x + node.width / 2, y: node.y + node.height },
            { x: node.x, y: node.y + node.height / 2 },
            { x: node.x + node.width, y: node.y + node.height / 2 }
        ];
        return positions[portIndex] || positions[1];
    }

    // Handle node mouse down
    function handleNodeMouseDown(e, node) {
        e.stopPropagation();
        selectNode(node);
        state.draggingNode = {
            node: node,
            offsetX: e.offsetX,
            offsetY: e.offsetY,
            startX: node.x,
            startY: node.y
        };
    }

    // Handle mouse move
    function handleMouseMove(e) {
        if (state.draggingNode) {
            const rect = container.getBoundingClientRect();
            const x = (e.clientX - rect.left - state.panX) / state.zoom;
            const y = (e.clientY - rect.top - state.panY) / state.zoom;

            state.draggingNode.node.x = snapToGrid(x - state.draggingNode.offsetX);
            state.draggingNode.node.y = snapToGrid(y - state.draggingNode.offsetY);

            updateNodePosition(state.draggingNode.node);
            updateConnections();
        }
    }

    // Handle mouse up
    function handleMouseUp(e) {
        if (state.draggingNode) {
            if (state.draggingNode.startX !== state.draggingNode.node.x ||
                state.draggingNode.startY !== state.draggingNode.node.y) {
                saveState();
                state.isDirty = true;
            }
            state.draggingNode = null;
        }
        if (state.connectingFrom) {
            state.connectingFrom = null;
            canvas.style.cursor = 'default';
        }
    }

    // Handle canvas click
    function handleCanvasClick(e) {
        if (e.target === canvas || e.target.parentElement === canvas) {
            deselectAll();
        }
    }

    // Handle keyboard shortcuts
    function handleKeyDown(e) {
        if (e.key === 'Delete' || e.key === 'Backspace') {
            if (state.selectedNode) {
                deleteNode(state.selectedNode);
            } else if (state.selectedConnection) {
                deleteConnection(state.selectedConnection);
            }
        } else if (e.ctrlKey || e.metaKey) {
            if (e.key === 'z') {
                e.preventDefault();
                if (e.shiftKey) redo(); else undo();
            } else if (e.key === 's') {
                e.preventDefault();
                save();
            }
        }
    }

    // Select a node
    function selectNode(node) {
        deselectAll();
        state.selectedNode = node;

        const element = document.getElementById(`node-${node.id}`);
        if (element) {
            element.classList.add('selected');
        }

        showNodeProperties(node);
    }

    // Select a connection
    function selectConnection(conn) {
        deselectAll();
        state.selectedConnection = conn;

        const element = document.getElementById(`conn-${conn.id}`);
        if (element) {
            element.classList.add('selected');
        }
    }

    // Deselect all
    function deselectAll() {
        state.selectedNode = null;
        state.selectedConnection = null;

        document.querySelectorAll('.workflow-node.selected, .connection.selected')
            .forEach(el => el.classList.remove('selected'));

        document.getElementById('propertiesContent').innerHTML =
            '<p class="placeholder-text">Select a node to view its properties</p>';
    }

    // Delete a node
    function deleteNode(node) {
        saveState();

        // Remove connections
        state.connections = state.connections.filter(c =>
            c.from.nodeId !== node.id && c.to.nodeId !== node.id
        );

        // Remove node
        state.nodes = state.nodes.filter(n => n.id !== node.id);

        // Re-render
        renderAll();
        deselectAll();
        state.isDirty = true;
    }

    // Delete a connection
    function deleteConnection(conn) {
        saveState();
        state.connections = state.connections.filter(c => c.id !== conn.id);
        document.getElementById(`conn-${conn.id}`)?.remove();
        deselectAll();
        state.isDirty = true;
    }

    // Show node properties panel
    function showNodeProperties(node) {
        const content = document.getElementById('propertiesContent');
        let template;

        if (node.type === 'condition') {
            template = document.getElementById('conditionPropertiesTemplate');
        } else if (node.type === 'trigger') {
            template = document.getElementById('triggerPropertiesTemplate');
        } else {
            template = document.getElementById('stepPropertiesTemplate');
        }

        if (template) {
            content.innerHTML = template.innerHTML;
            populateProperties(node);
        }
    }

    // Populate properties form
    function populateProperties(node) {
        const props = node.properties || {};
        Object.keys(props).forEach(key => {
            const input = document.getElementById(`prop${capitalize(key)}`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = props[key];
                } else {
                    input.value = props[key];
                }
            }
        });
    }

    // Handle property change
    function handlePropertyChange(e) {
        if (!state.selectedNode) return;

        const input = e.target;
        const propName = input.id.replace('prop', '').toLowerCase();

        saveState();

        if (!state.selectedNode.properties) {
            state.selectedNode.properties = {};
        }

        state.selectedNode.properties[propName] = input.type === 'checkbox' ? input.checked : input.value;

        if (propName === 'name') {
            state.selectedNode.label = input.value;
            updateNodeLabel(state.selectedNode);
        }

        state.isDirty = true;
    }

    // Update node position in DOM
    function updateNodePosition(node) {
        const element = document.getElementById(`node-${node.id}`);
        if (element) {
            element.setAttribute('transform', `translate(${node.x}, ${node.y})`);
        }
    }

    // Update node label
    function updateNodeLabel(node) {
        const element = document.getElementById(`node-${node.id}`);
        if (element) {
            const text = element.querySelector('text');
            if (text) text.textContent = node.label;
        }
    }

    // Update all connections
    function updateConnections() {
        state.connections.forEach(conn => {
            const element = document.getElementById(`conn-${conn.id}`);
            if (element) {
                const fromNode = state.nodes.find(n => n.id === conn.from.nodeId);
                const toNode = state.nodes.find(n => n.id === conn.to.nodeId);
                if (fromNode && toNode) {
                    const fromPort = getPortPosition(fromNode, conn.from.port);
                    const toPort = getPortPosition(toNode, conn.to.port);
                    element.setAttribute('d', calculatePath(fromPort, toPort));
                }
            }
        });
    }

    // Render all nodes and connections
    function renderAll() {
        nodesLayer.innerHTML = '';
        connectionsLayer.innerHTML = '';
        state.nodes.forEach(node => renderNode(node));
        state.connections.forEach(conn => renderConnection(conn));
    }

    // Save state for undo
    function saveState() {
        state.undoStack.push(JSON.stringify({ nodes: state.nodes, connections: state.connections }));
        state.redoStack = [];
        if (state.undoStack.length > 50) state.undoStack.shift();
    }

    // Undo
    function undo() {
        if (state.undoStack.length === 0) return;
        state.redoStack.push(JSON.stringify({ nodes: state.nodes, connections: state.connections }));
        const prev = JSON.parse(state.undoStack.pop());
        state.nodes = prev.nodes;
        state.connections = prev.connections;
        renderAll();
        deselectAll();
    }

    // Redo
    function redo() {
        if (state.redoStack.length === 0) return;
        state.undoStack.push(JSON.stringify({ nodes: state.nodes, connections: state.connections }));
        const next = JSON.parse(state.redoStack.pop());
        state.nodes = next.nodes;
        state.connections = next.connections;
        renderAll();
        deselectAll();
    }

    // Zoom controls
    function zoomIn() {
        state.zoom = Math.min(state.zoom + config.zoomStep, config.zoomMax);
        applyZoom();
    }

    function zoomOut() {
        state.zoom = Math.max(state.zoom - config.zoomStep, config.zoomMin);
        applyZoom();
    }

    function fitToScreen() {
        state.zoom = 1;
        state.panX = 0;
        state.panY = 0;
        applyZoom();
    }

    function applyZoom() {
        nodesLayer.setAttribute('transform', `translate(${state.panX}, ${state.panY}) scale(${state.zoom})`);
        connectionsLayer.setAttribute('transform', `translate(${state.panX}, ${state.panY}) scale(${state.zoom})`);
    }

    // Update canvas size
    function updateCanvasSize() {
        const rect = container.getBoundingClientRect();
        canvas.setAttribute('width', rect.width);
        canvas.setAttribute('height', rect.height);
    }

    // Save workflow
    function save() {
        const definition = {
            nodes: state.nodes,
            connections: state.connections,
            version: '1.0'
        };

        fetch(config.saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({
                workflow_id: config.workflowId,
                definition: definition
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                state.isDirty = false;
                alert('Workflow saved successfully!');
            } else {
                alert('Error saving workflow: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            alert('Error saving workflow');
        });
    }

    // Load workflow definition
    function loadDefinition(definition) {
        if (!definition) return;
        state.nodes = definition.nodes || [];
        state.connections = definition.connections || [];
        renderAll();
    }

    // Get default properties for node type
    function getDefaultProperties(type) {
        const defaults = {
            step: { name: 'Process Step', description: '', status: 'RECEIVED', requiresQC: false, duration: 1 },
            condition: { conditionName: 'Condition', field: 'interpretation', operator: 'eq', value: '' },
            trigger: { triggerName: 'Trigger Test', testPanel: '', autoApprove: false, notifyPhysician: true }
        };
        return defaults[type] || { name: nodeTypes[type]?.label || 'Node' };
    }

    // Utility functions
    function generateId() {
        return 'n' + Math.random().toString(36).substr(2, 9);
    }

    function snapToGrid(value) {
        return Math.round(value / config.gridSize) * config.gridSize;
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Export definition
    function exportDefinition() {
        return {
            nodes: state.nodes,
            connections: state.connections,
            version: '1.0'
        };
    }

    // Public API
    return {
        init,
        addNode,
        deleteNode,
        undo,
        redo,
        zoomIn,
        zoomOut,
        fitToScreen,
        save,
        loadDefinition,
        exportDefinition,
        getState: () => state
    };
})();
