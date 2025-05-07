function getRequestData() {
    return {
        buildings: Array.from(document.getElementById('building-select').selectedOptions).map(opt => opt.value),
        energy_type: document.getElementById('energy-type').value,
        time_range: document.getElementById('time-range').value,
        start_date: document.getElementById('start-date').value,
        end_date: document.getElementById('end-date').value
    };
}

function updateEnergyChart() {
    fetch('/get_energy_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(getRequestData())
    })
    .then(res => res.json())
    .then(energyData => {
        Plotly.newPlot('energyChartDiv', energyData.traces, { title: 'Energy Usage' });
    })
    .catch(error => {
        console.error('Error fetching energy data:', error);
    });
}

const updateCo2Chart = () => {
    const selectedBuildings = Array.from(document.getElementById('building-select-co2').selectedOptions).map(opt => opt.value);
    const selectedEnergyType = document.getElementById('co2-emission').value;
    const selectedTimeRange = document.getElementById('time-range-co2').value;
    const startDate = document.getElementById('start-date-co2').value;
    const endDate = document.getElementById('end-date-co2').value;

    const requestData = {
        buildings: selectedBuildings,
        energy_type: selectedEnergyType,
        time_range: selectedTimeRange,
        start_date: startDate,
        end_date: endDate
    };

    fetch('/get_co2_energy_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(res => res.json())
    .then(data => {
        Plotly.newPlot('co2ChartDiv', data.traces, { title: 'Kg CO₂ per kWh Emissions' });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
};

// Attach event listener to the filter controls
document.getElementById('building-select-co2').addEventListener('change', updateCo2Chart);
document.getElementById('co2-emission').addEventListener('change', updateCo2Chart);
document.getElementById('time-range-co2').addEventListener('change', updateCo2Chart);
document.getElementById('start-date-co2').addEventListener('change', updateCo2Chart);
document.getElementById('end-date-co2').addEventListener('change', updateCo2Chart);


// Initial load
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('building-select').options[0].selected = true;
    updateEnergyChart();
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('building-select-co2').options[0].selected = true;
    updateCo2Chart();
});

document.getElementById('building-select').addEventListener('change', () => {
    updateEnergyChart();
});
document.getElementById('energy-type').addEventListener('change', updateEnergyChart);
document.getElementById('time-range').addEventListener('change', updateEnergyChart);
document.getElementById('start-date').addEventListener('change', () => {
    updateEnergyChart();
});
document.getElementById('end-date').addEventListener('change', () => {
    updateEnergyChart();
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