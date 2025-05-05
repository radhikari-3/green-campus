function updateChart() {
    var timeRange = document.getElementById('time-range').value;
    var buildingSelect = document.getElementById('building-select');
    var selectedBuildings = Array.from(buildingSelect.selectedOptions).map(option => option.value);
    var energyType = document.getElementById('energy-type').value;

    if (timeRange === 'custom') {
        document.getElementById('custom-date-range').style.display = 'block';
    } else {
        document.getElementById('custom-date-range').style.display = 'none';
    }

    fetch('/get_energy_data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            time_range: timeRange,
            start_date: document.getElementById('start-date').value,
            end_date: document.getElementById('end-date').value,
            buildings: selectedBuildings,
            energy_type: energyType
        })
    })
    .then(response => response.json())
    .then(data => {
        Plotly.newPlot('energy-chart', data.traces, {
            title: 'Energy Usage Over Time',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Energy (kWh)' },
            responsive: true
        });
    });
}

// Initial load
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('building-select').options[0].selected = true;
    updateChart();
});

// Fuel Type Usage Chart (Electricity vs Gas)
const fuelUsage = window.totalUsageByZones;
const electricityData = fuelUsage.electricity_usage;
const gasData = fuelUsage.gas_usage;

const fuelTraceElectricity = {
    x: electricityData.labels,
    y: electricityData.data,
    type: 'bar',
    name: 'Electricity',
    marker: { color: '#1f77b4' }  // Blue for electricity
};

const fuelTraceGas = {
    x: gasData.labels,
    y: gasData.data,
    type: 'bar',
    name: 'Gas',
    marker: { color: '#ff7f0e' }  // Orange for gas
};

const fuelLayout = {
    title: 'Zonal Energy Usage by Fuel Type',
    barmode: 'group',
    xaxis: { title: 'Zones' },
    yaxis: { title: 'Energy Usage (kWh)' },
    showlegend: true,
    responsive: true
};

Plotly.newPlot('fuelTypeChart', [fuelTraceElectricity, fuelTraceGas], fuelLayout);