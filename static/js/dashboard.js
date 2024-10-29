let myChart; 
document.addEventListener('DOMContentLoaded', () => {
    const initialCheckId = document.getElementById('initial-check-id').value; // Get the ID of the first check
    openChart(initialCheckId);
});

function openChart(checkId) {
    fetch(`/api/chart-data/${checkId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(JSON.stringify(data))
            const labels = data.labels.slice(-10);
            const datas = data.data.slice(-10);
            const statusCodes = data.statuses ? data.statuses.slice(-10) : []; // Use 'statuses'

            if (Array.isArray(labels) && Array.isArray(datas) && Array.isArray(statusCodes)) {
                
                const chartData = {
                    labels: labels,
                    datasets: [{
                        label: 'Response Time',
                        data: datas,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        pointBackgroundColor: statusCodes.map(status => status === '200' ? 'green' : 'red'), // Point color based on status
                        borderWidth: 1,
                        fill: false 
                    }]
                };

                createChart(chartData);
            } else {
                console.error('Invalid data format:', data);
                alert('Error: Invalid data format received.');
            }
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            alert('Error fetching chart data. Please try again later.');
        });
}

function createChart(chartData) {
    const ctx = document.getElementById('responseChart').getContext('2d');

    if (myChart) {
        myChart.destroy();
    }

    myChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Response Time (ms)' // Y-axis title
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Previous Checked' // X-axis title
                    },
                    ticks: {
                        display: false // Disable x-axis labels
                    },
                }
            }
        }
    });
}
