let myChart;
document.addEventListener('DOMContentLoaded', () => {
    const initialCheckId = document.getElementById('initial-check-id').value;
    openChart(initialCheckId);
});

function openChart(checkId) {
    fetch(`/api/chart-data/${checkId}/`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            console.log("Response Data ->", data);  // Log the full data

            // Prepare the datasets dynamically based on the locations (keys in the response)
            const datasets = [];
            let labels = [];
            let isFirstLocation = true;  // Flag to ensure we only use the first location's labels

            // Define an array of colors (can be expanded if needed)
            const colors = [
                'rgba(75, 192, 192, 1)', // Teal
                'rgba(153, 102, 255, 1)', // Purple
                'rgba(255, 159, 64, 1)', // Orange
                'rgba(255, 205, 86, 1)', // Yellow
                'rgba(54, 162, 235, 1)', // Blue
                'rgba(201, 203, 207, 1)'  // Grey
            ];

            let colorIndex = 0; // To cycle through the colors

            // Loop through each location in the response data (e.g., 'ca', 'us', etc.)
            for (const location in data) {
                const locationData = data[location];  // Access each location's data
                const locationLabels = locationData.labels.slice(-10);
                const locationDataPoints = locationData.data.slice(-10);
                const statusCodes = locationData.statuses ? locationData.statuses.slice(-10) : [];

                // Set labels for the first location (assume all locations have the same labels)
                if (isFirstLocation) {
                    labels = locationLabels;
                    isFirstLocation = false;
                }

                // Only proceed if the data format is valid
                if (Array.isArray(locationLabels) && Array.isArray(locationDataPoints) && Array.isArray(statusCodes)) {
                    datasets.push({
                        label: location,  // Use the location as the dataset label (e.g., 'ca', 'us')
                        data: locationDataPoints,
                        borderColor: colors[colorIndex % colors.length],  // Assign a color from the colors array
                        pointBackgroundColor: statusCodes.map(status => status === '200' ? 'green' : 'red'),
                        borderWidth: 1,
                        fill: false
                    });

                    // Cycle through the colors for the next location
                    colorIndex++;
                } else {
                    alert('Error: Invalid data format received for ' + location);
                }
            }

            // Create chart if we have at least one valid dataset
            if (datasets.length > 0) {
                const chartData = {
                    labels: labels,  // Same labels for all datasets
                    datasets: datasets  // Dynamic datasets with different line colors
                };
                createChart(chartData);
            } else {
                alert('Error: No valid data for chart creation.');
            }
        })
        .catch(error => alert('Error fetching chart data. Please try again later.'));
}

function createChart(chartData) {
    const ctx = document.getElementById('responseChart').getContext('2d');

    if (myChart) myChart.destroy();

    myChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Response Time (ms)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Previous Checked'
                    },
                    ticks: {
                        display: false
                    },
                }
            }
        }
    });
}

let currentCheckId;
function openEditForm(checkId, event) {
    currentCheckId = checkId;
    event.stopPropagation();
    openEditPopup(checkId);
}

function openEditPopup(checkId) {
    fetch(`/api/check/${checkId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("id_name_of_check").value = data.name_of_check;
            document.getElementById("id_check_interval").value = data.check_interval;
            document.getElementById("id_check_type").value = data.check_type;
            document.getElementById("id_url").value = data.url;
            document.getElementById("id_contact_detail").value = data.contact_detail;

            const selectedLocations = data.location_to_check;
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name="location_to_check"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectedLocations.includes(checkbox.value);
            });

            document.getElementById("editFormPopup").style.display = "flex";
        });
}

function closePopup() {
    document.getElementById("editFormPopup").style.display = "none";
}

function saveEditForm() {
    try {
        const locationCheckboxes = document.querySelectorAll("input[name='location_to_check']:checked");
        const selectedLocations = Array.from(locationCheckboxes).map(checkbox => checkbox.value);

        const formData = {
            id: currentCheckId,
            name_of_check: document.getElementById("id_name_of_check").value || "",
            check_interval: document.getElementById("id_check_interval").value || "",
            check_type: document.getElementById("id_check_type").value || "",
            url: document.getElementById("id_url").value || "",
            contact_detail: document.getElementById("id_contact_detail").value || "",
            location_to_check: selectedLocations
        };

        if (!formData.location_to_check.length) {
            alert("Please select at least one location.");
            return;
        }

        fetch(`http://127.0.0.1:8000/api/check/${currentCheckId}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(() => {
            alert("Check updated successfully!");
            closePopup();
        })
        .catch(() => alert("Failed to update check. Please try again."));
    } catch {
        alert("An unexpected error occurred. Please check the form and try again.");
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function filterCountries() {
    const input = document.getElementById('searchLocation');
    const filter = input.value.toLowerCase();
    const options = document.querySelectorAll('.country-option');
    
    options.forEach(option => {
        const label = option.querySelector('label').innerText.toLowerCase();
        option.style.display = label.includes(filter) ? '' : 'none';
    });
}
