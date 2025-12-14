/**
 * Finance App - Chart Utilities
 */

// Format currency
function formatCurrency(value) {
    if (value === undefined || value === null) return '£0.00';
    const absValue = Math.abs(value);
    const formatted = absValue.toLocaleString('en-GB', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return (value < 0 ? '-' : '') + '£' + formatted;
}

// Chart.js default config
Chart.defaults.color = '#95a5a6';
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";

// Common chart colors
const chartColors = {
    blue: '#3498db',
    red: '#e74c3c',
    green: '#2ecc71',
    yellow: '#f1c40f',
    purple: '#9b59b6',
    teal: '#1abc9c',
    orange: '#e67e22',
};

// Palette for multiple datasets
const colorPalette = [
    chartColors.blue,
    chartColors.red,
    chartColors.green,
    chartColors.yellow,
    chartColors.purple,
    chartColors.teal,
    chartColors.orange,
    '#34495e',
    '#16a085',
    '#c0392b',
];

// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#ecf0f1',
                padding: 20,
                usePointStyle: true,
            }
        },
        tooltip: {
            backgroundColor: '#1a1f2e',
            titleColor: '#ecf0f1',
            bodyColor: '#95a5a6',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            callbacks: {
                label: function (context) {
                    return context.dataset.label + ': ' + formatCurrency(context.raw);
                }
            }
        }
    },
    scales: {
        x: {
            ticks: { color: '#95a5a6' },
            grid: { color: 'rgba(255,255,255,0.05)' }
        },
        y: {
            ticks: {
                color: '#95a5a6',
                callback: function (value) {
                    return '£' + value.toLocaleString();
                }
            },
            grid: { color: 'rgba(255,255,255,0.05)' }
        }
    }
};

// Helper to create line chart
function createLineChart(ctx, labels, datasets) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map((ds, i) => ({
                ...ds,
                borderColor: ds.borderColor || colorPalette[i],
                backgroundColor: (ds.borderColor || colorPalette[i]) + '20',
                fill: ds.fill !== undefined ? ds.fill : true,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6,
            }))
        },
        options: commonOptions
    });
}

// Helper to create bar chart
function createBarChart(ctx, labels, datasets) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets.map((ds, i) => ({
                ...ds,
                backgroundColor: (ds.backgroundColor || colorPalette[i]) + 'cc',
                borderColor: ds.borderColor || colorPalette[i],
                borderWidth: 1,
                borderRadius: 4,
            }))
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                x: {
                    ...commonOptions.scales.x,
                    grid: { display: false }
                }
            }
        }
    });
}

// Helper to create doughnut chart
function createDoughnutChart(ctx, labels, data, colors) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors || colorPalette,
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#ecf0f1',
                        padding: 15,
                        usePointStyle: true,
                    }
                },
                tooltip: commonOptions.plugins.tooltip
            }
        }
    });
}

console.log('Charts.js loaded');
