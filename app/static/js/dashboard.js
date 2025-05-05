const walkingData = JSON.parse(document.querySelector('script[data-walking-data]').dataset.walkingData || '[]');
const cyclingData = JSON.parse(document.querySelector('script[data-cycling-data]').dataset.cyclingData || '[]');
const avgData = JSON.parse(document.querySelector('script[data-avg-data]').dataset.avgData || '[]');
const avgCyclingData = JSON.parse(document.querySelector('script[data-avg-cycling-data]').dataset.avgCyclingData || '[]');

const allDates = [...new Set([
  ...walkingData.map(d => d.date),
  ...cyclingData.map(d => d.date)
])].sort();

function filterByRange(data, days) {
  if (days === 'all') return data;
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - parseInt(days));
  return data.filter(d => new Date(d.x) >= cutoff);
}

const getDatasets = (type, range) => {
  const source = type === 'steps' ? walkingData : cyclingData;
  const avg = type === 'steps' ? avgData : avgCyclingData;

  const dataUser = allDates.map(date => {
    const entry = source.find(e => e.date === date);
    return entry ? { x: date, y: type === 'steps' ? entry.steps : entry.distance, eco: entry.eco || 0 } : { x: date, y: 0, eco: 0 };
  });

  const dataAvg = allDates.map(date => {
    const entry = avg.find(e => e.date === date);
    return entry ? { x: date, y: type === 'steps' ? entry.steps : entry.distance } : { x: date, y: 0 };
  });

  return {
    user: filterByRange(dataUser, range),
    avg: filterByRange(dataAvg, range)
  };
};

const ctx = document.getElementById("mainChart").getContext("2d");
let chart;

function updateGraph() {
  const type = document.getElementById("dataSelection").value;
  const range = document.getElementById("rangeSelection").value;

  const { user, avg } = getDatasets(type, range);
  const labels = user.map(e => e.x);

  chart.data.labels = labels;
  chart.data.datasets[0].data = user;
  chart.data.datasets[1].data = avg;
  chart.data.datasets[0].label = type === 'steps' ? 'Your Steps' : 'Your Cycling Distance';
  chart.data.datasets[1].label = type === 'steps' ? 'Average Steps' : 'Average Cycling Distance';
  chart.data.datasets[0].borderColor = type === 'steps' ? `#3b82f6` : `#10b981`;
  chart.data.datasets[1].borderColor = type === 'steps' ? `#f59e0b` : `#6b7280`;

  chart.update();
}

const initial = getDatasets('steps', 'all');
chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: initial.user.map(e => e.x),
    datasets: [
      {
        label: "Your Steps",
        data: initial.user,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 8
      },
      {
        label: "Average Steps",
        data: initial.avg,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 8
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        position: 'top',
        labels: { font: { size: 14, family: 'Inter' }, padding: 20 }
      },
      tooltip: {
        backgroundColor: '#1a2b49',
        titleFont: { size: 14, family: 'Inter' },
        bodyFont: { size: 12, family: 'Inter' },
        callbacks: {
          label: function(context) {
            const { raw, dataset } = context;
            if (raw && typeof raw === 'object' && 'eco' in raw) {
              return `${dataset.label}: ${raw.y} (Eco Points: ${raw.eco})`;
            }
            return `${dataset.label}: ${raw.y ?? raw}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Value',
          font: { size: 14, family: 'Inter' }
        },
        grid: { color: 'rgba(0,0,0,0.05)' }
      },
      x: {
        title: {
          display: true,
          text: 'Date',
          font: { size: 14, family: 'Inter' }
        },
        grid: { display: false }
      }
    }
  }
});