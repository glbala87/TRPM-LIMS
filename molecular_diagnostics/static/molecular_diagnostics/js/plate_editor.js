/**
 * PCR Plate Layout Editor
 * Provides interactive plate visualization and sample assignment
 */

class PlateEditor {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.plateType = options.plateType || '96';
        this.plateId = options.plateId || null;
        this.readonly = options.readonly || false;
        this.onWellClick = options.onWellClick || null;
        this.onLayoutChange = options.onLayoutChange || null;

        this.rows = this.plateType === '96' ? 8 : 16;
        this.cols = this.plateType === '96' ? 12 : 24;
        this.rowLabels = 'ABCDEFGHIJKLMNOP'.substring(0, this.rows).split('');

        this.layout = {};
        this.selectedWells = new Set();

        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();

        if (this.plateId) {
            this.loadLayout();
        }
    }

    render() {
        const table = document.createElement('table');
        table.className = 'plate-layout';

        // Header row with column numbers
        const headerRow = document.createElement('tr');
        headerRow.appendChild(document.createElement('th')); // Empty corner cell

        for (let col = 1; col <= this.cols; col++) {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        }
        table.appendChild(headerRow);

        // Data rows
        for (let row = 0; row < this.rows; row++) {
            const tr = document.createElement('tr');

            // Row label
            const rowLabel = document.createElement('th');
            rowLabel.textContent = this.rowLabels[row];
            tr.appendChild(rowLabel);

            // Wells
            for (let col = 1; col <= this.cols; col++) {
                const position = `${this.rowLabels[row]}${col}`;
                const td = document.createElement('td');
                td.className = 'well empty';
                td.dataset.position = position;
                td.title = position;

                const wellContent = document.createElement('div');
                wellContent.className = 'well-content';
                td.appendChild(wellContent);

                tr.appendChild(td);
            }

            table.appendChild(tr);
        }

        this.container.innerHTML = '';
        this.container.appendChild(table);

        // Add styles
        this.addStyles();
    }

    addStyles() {
        if (document.getElementById('plate-editor-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'plate-editor-styles';
        styles.textContent = `
            .plate-layout {
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 11px;
            }

            .plate-layout th {
                padding: 4px 6px;
                background: #f5f5f5;
                border: 1px solid #ddd;
                font-weight: bold;
                text-align: center;
            }

            .plate-layout .well {
                width: 28px;
                height: 28px;
                border: 1px solid #ccc;
                border-radius: 50%;
                cursor: pointer;
                text-align: center;
                vertical-align: middle;
                transition: all 0.15s ease;
            }

            .plate-layout .well:hover {
                border-color: #666;
                box-shadow: 0 0 4px rgba(0,0,0,0.2);
            }

            .plate-layout .well.selected {
                border: 2px solid #2196F3;
                box-shadow: 0 0 6px rgba(33, 150, 243, 0.5);
            }

            .plate-layout .well.empty {
                background: #fff;
            }

            .plate-layout .well.sample {
                background: #4CAF50;
            }

            .plate-layout .well.positive {
                background: #FF9800;
            }

            .plate-layout .well.negative {
                background: #2196F3;
            }

            .plate-layout .well.ntc {
                background: #9E9E9E;
            }

            .plate-layout .well.calibrator {
                background: #9C27B0;
            }

            .plate-layout .well-content {
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 9px;
            }

            .plate-legend {
                margin-top: 10px;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }

            .plate-legend .legend-item {
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 12px;
            }

            .plate-legend .legend-color {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                border: 1px solid #ccc;
            }
        `;
        document.head.appendChild(styles);
    }

    attachEventListeners() {
        this.container.addEventListener('click', (e) => {
            const well = e.target.closest('.well');
            if (!well) return;

            const position = well.dataset.position;

            if (e.shiftKey) {
                // Multi-select with shift
                this.toggleWellSelection(position);
            } else if (e.ctrlKey || e.metaKey) {
                // Add to selection with ctrl/cmd
                this.toggleWellSelection(position);
            } else {
                // Single select
                this.clearSelection();
                this.toggleWellSelection(position);
            }

            if (this.onWellClick) {
                this.onWellClick(position, this.layout[position], this.selectedWells);
            }
        });
    }

    toggleWellSelection(position) {
        const well = this.container.querySelector(`[data-position="${position}"]`);
        if (!well) return;

        if (this.selectedWells.has(position)) {
            this.selectedWells.delete(position);
            well.classList.remove('selected');
        } else {
            this.selectedWells.add(position);
            well.classList.add('selected');
        }
    }

    clearSelection() {
        this.selectedWells.forEach(pos => {
            const well = this.container.querySelector(`[data-position="${pos}"]`);
            if (well) well.classList.remove('selected');
        });
        this.selectedWells.clear();
    }

    setWell(position, data) {
        this.layout[position] = data;
        this.updateWellDisplay(position);

        if (this.onLayoutChange) {
            this.onLayoutChange(this.layout);
        }
    }

    updateWellDisplay(position) {
        const well = this.container.querySelector(`[data-position="${position}"]`);
        if (!well) return;

        const data = this.layout[position] || {};
        const content = well.querySelector('.well-content');

        // Reset classes
        well.className = 'well';

        if (data.control_type) {
            switch (data.control_type) {
                case 'POSITIVE':
                    well.classList.add('positive');
                    content.textContent = '+';
                    break;
                case 'NEGATIVE':
                    well.classList.add('negative');
                    content.textContent = '-';
                    break;
                case 'NTC':
                    well.classList.add('ntc');
                    content.textContent = 'N';
                    break;
                case 'CALIBRATOR':
                    well.classList.add('calibrator');
                    content.textContent = 'C';
                    break;
                case 'EMPTY':
                    well.classList.add('empty');
                    content.textContent = '';
                    break;
            }
        } else if (data.sample_id) {
            well.classList.add('sample');
            // Show abbreviated sample ID
            content.textContent = data.sample_id.slice(-4);
            well.title = `${position}: ${data.sample_id}`;
        } else {
            well.classList.add('empty');
            content.textContent = '';
        }
    }

    async loadLayout() {
        try {
            const response = await fetch(`/molecular/plates/${this.plateId}/layout/`);
            const data = await response.json();

            this.layout = data.layout || {};

            Object.keys(this.layout).forEach(position => {
                this.updateWellDisplay(position);
            });
        } catch (error) {
            console.error('Error loading plate layout:', error);
        }
    }

    getLayout() {
        return this.layout;
    }

    getSelectedWells() {
        return Array.from(this.selectedWells);
    }

    assignSampleToSelected(sampleId) {
        this.selectedWells.forEach(position => {
            this.setWell(position, { sample_id: sampleId });
        });
    }

    assignControlToSelected(controlType) {
        this.selectedWells.forEach(position => {
            this.setWell(position, { control_type: controlType });
        });
    }

    clearSelectedWells() {
        this.selectedWells.forEach(position => {
            this.setWell(position, {});
        });
    }

    renderLegend() {
        const legend = document.createElement('div');
        legend.className = 'plate-legend';

        const items = [
            { color: '#fff', label: 'Empty' },
            { color: '#4CAF50', label: 'Sample' },
            { color: '#FF9800', label: 'Positive Control' },
            { color: '#2196F3', label: 'Negative Control' },
            { color: '#9E9E9E', label: 'NTC' },
            { color: '#9C27B0', label: 'Calibrator' },
        ];

        items.forEach(item => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            legendItem.innerHTML = `
                <div class="legend-color" style="background: ${item.color}"></div>
                <span>${item.label}</span>
            `;
            legend.appendChild(legendItem);
        });

        this.container.appendChild(legend);
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PlateEditor;
}
