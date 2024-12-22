let myChart;
document.addEventListener('DOMContentLoaded', () => {
    const initialCheckId = document.getElementById('initial-check-id').value;
    openChart(initialCheckId);
    fetchLocationsAndStatuses(initialCheckId);
    fetchAndUpdateSSLDomainData(initialCheckId);
});
function handleCardClick(checkId){
    openChart(checkId)
    fetchLocationsAndStatuses(checkId)
    fetchAndUpdateSSLDomainData(checkId);
    const subCardContainer = document.querySelector('.sub-card-container');
    subCardContainer.classList.add('visible');
}
function openChart(checkId) {
    fetch(`/api/chart-data/${checkId}/`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
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

            let colorIndex = 0;

            for (const location in data) {
                const locationData = data[location];  // Access each location's data
                const locationLabels = locationData.labels.slice(-10);
                const locationDataPoints = locationData.data.slice(-10);
                const statusCodes = locationData.statuses ? locationData.statuses.slice(-10) : [];

                if (isFirstLocation) {
                    labels = locationLabels;
                    isFirstLocation = false;
                }

                if (Array.isArray(locationLabels) && Array.isArray(locationDataPoints) && Array.isArray(statusCodes)) {
                    datasets.push({
                        label: location,
                        data: locationDataPoints,
                        borderColor: colors[colorIndex % colors.length],
                        pointBackgroundColor: statusCodes.map(status => status === '200' ? 'green' : 'red'),
                        borderWidth: 1,
                        fill: false
                    });

                    colorIndex++;
                } else {
                    alert('Error: Invalid data format received for ' + location);
                }
            }

            if (datasets.length > 0) {
                const chartData = {
                    labels: labels,
                    datasets: datasets
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
            document.getElementById("id_port").value = data.port;
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
        const port = parseInt(document.getElementById("id_port").value, 10);
        if (isNaN(port) || port < 0 || port > 65535) {
            alert("Please enter a valid port number between 0 and 65535.");
            return;
        }
        const formData = {
            id: currentCheckId,
            name_of_check: document.getElementById("id_name_of_check").value || "",
            check_interval: document.getElementById("id_check_interval").value || "",
            check_type: document.getElementById("id_check_type").value || "",
            url: document.getElementById("id_url").value || "",
            port: port,
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
            showSuccessPopupWithCountdown("Updated Successfully!");
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

let selectedCheckId = null;
let selectedCheckName = null;

function deleteCheck(checkId, checkName, event) {
    event.stopPropagation();
    selectedCheckId = checkId;
    selectedCheckName = checkName;
    showModal();
}

function showModal() {
    const modalContent = document.querySelector("#deleteModal .modal-content p");
    modalContent.innerHTML = `Are you sure you want to delete the check: <strong>${selectedCheckName}</strong>?`;

    const modal = document.getElementById("deleteModal");
    modal.style.display = "block";

    const confirmButton = document.getElementById("confirmDeleteButton");
    confirmButton.onclick = () => confirmDeleteAction();
}

function closeModal() {
    const modal = document.getElementById("deleteModal");
    modal.style.display = "none";
    selectedCheckId = null;
    selectedCheckName = null;
}

function confirmDeleteAction() {
    if (!selectedCheckId) return;

    fetch(`/api/check/${selectedCheckId}/`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        closeModal();
        showSuccessPopupWithCountdown("Deleted successfully!");
    })
    .catch(() => {
        alert("Failed to delete the check. Please try again.");
        closeModal();
    });
}

function showSuccessPopupWithCountdown(message) {
    const successPopup = document.getElementById("successPopup");
    const successMessage = document.getElementById("successMessage");
    const countdownElement = document.getElementById("countdown");
    const overlay = document.getElementById("overlay");

    successMessage.innerText = message;

    successPopup.style.display = "block";
    overlay.style.display = "block";
    
    let countdown = 3;
    countdownElement.innerText = countdown;

    const countdownInterval = setInterval(() => {
        countdown--;
        countdownElement.innerText = countdown;
        if (countdown === 0) {
            clearInterval(countdownInterval);
            setTimeout(() => {
                successPopup.style.display = "none";
                overlay.style.display = "none";
                location.reload();
            }, 500);
        }
    }, 1000);
}

function fetchLocationsAndStatuses(checkId) {
    const apiUrl = `/api/port-ping-data/${checkId}/`; // Dynamic API URL

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const cardContainer = document.querySelector('.sub-card-container');
            cardContainer.innerHTML = '';

            for (const location in data) {
                const locationData = data[location];

                if (!locationData.ping_status || !locationData.port_status || locationData.ping_status.length === 0 || locationData.port_status.length === 0) {
                    console.warn(`No data available for location: ${location}`);
                    continue;
                }

                const latestEntryPingStatus = locationData.ping_status[locationData.ping_status.length - 1];
                const latestEntryPortStatus = locationData.port_status[locationData.port_status.length - 1];

                const card = document.createElement('div');
                card.classList.add('sub-card');

                const locationName = document.createElement('h2');
                const formattedLocation = location.toUpperCase();
                locationName.textContent = formattedLocation;
                card.appendChild(locationName);

                const latestStatus = document.createElement('div');
                latestStatus.classList.add('latest-status');

                // Ping Status Section
                const pingStatusContainer = document.createElement('div');
                pingStatusContainer.classList.add('status-container'); // Create a container for Ping

                const pingStatus = document.createElement('span');
                pingStatus.classList.add('status-indicator-pp');

                const pingText = document.createElement('span');
                pingText.textContent = 'Ping: ';
                pingText.style.color = 'black';

                const statusText = document.createElement('span');
                statusText.textContent = latestEntryPingStatus;
                statusText.classList.add(
                    latestEntryPingStatus === 'Reachable' ? 'status-up' : 'status-down'
                );

                pingStatus.appendChild(pingText);
                pingStatus.appendChild(statusText);
                pingStatusContainer.appendChild(pingStatus); // Append to the container

                // Port Status Section
                const portStatusContainer = document.createElement('div');
                portStatusContainer.classList.add('status-container'); // Create a container for Port

                const portStatus = document.createElement('span');
                portStatus.classList.add('status-indicator-pp');

                const portText = document.createElement('span');
                portText.textContent = 'Port: ';
                portText.style.color = 'black';

                const portStatusText = document.createElement('span');
                portStatusText.textContent = latestEntryPortStatus;
                portStatusText.classList.add(
                    latestEntryPortStatus === 'Open' ? 'status-up' : 'status-down'
                );

                portStatus.appendChild(portText);
                portStatus.appendChild(portStatusText);
                portStatusContainer.appendChild(portStatus); // Append to the container

                // Append both Ping and Port Status Containers to the latestStatus
                latestStatus.appendChild(pingStatusContainer);
                latestStatus.appendChild(portStatusContainer);

                card.appendChild(latestStatus);

                cardContainer.appendChild(card);
            }
        })
        .catch(error => {
            console.error('Error fetching location data:', error);
            alert('Error fetching location data. Please try again later.');
        });
}

function fetchAndUpdateSSLDomainData(checkId) {
    const apiUrl = `/api/ssl-domain-data/${checkId}/`;

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch SSL/Domain data.");
            }
            return response.json();
        })
        .then(data => {
            const sslContainer = document.querySelector(".ssl-status .info-content");
            const domainContainer = document.querySelector(".domain-expiry .info-content");

            const sslExpiryDate = data.ssl_expiry_date[data.ssl_expiry_date.length - 1];
            const currentDate = new Date();
            const expiryDate = new Date(sslExpiryDate);

            let sslStatus = "Active";
            if (expiryDate <= currentDate) {
                sslStatus = "Expired";
            }

            const statusElement = sslContainer.querySelector(".status");
            statusElement.innerText = `${sslStatus}`;            if (sslStatus === "Active") {
                statusElement.style.color = "green";
            } else if (sslStatus === "Expired") {
                statusElement.style.color = "red";
            }
            sslContainer.querySelector("p:nth-child(3)").innerText = `Expires: ${sslExpiryDate}`;
            const domainExpiryDate = data.domain_expiry_date[data.domain_expiry_date.length - 1];
            const timeRemaining = getTimeUntilExpiry(domainExpiryDate);

            domainContainer.querySelector(".status").innerText = `Expires in ${timeRemaining.years} years, ${timeRemaining.months} months, ${timeRemaining.days} days`;
            domainContainer.querySelector("p:nth-child(3)").innerText = `Renewal Date: ${data.domain_expiry_date[data.domain_expiry_date.length - 1]}`;
        })
        .catch(error => {
            console.error("Error updating SSL/Domain status:", error);
            alert("Failed to update SSL/Domain status.");
        });
}

function getTimeUntilExpiry(expiryDate) {
    const currentDate = new Date();
    const domainExpiryDate = new Date(expiryDate);
    
    const timeDifference = domainExpiryDate - currentDate;
    
    const daysRemaining = Math.floor(timeDifference / (1000 * 3600 * 24));
    
    const years = Math.floor(daysRemaining / 365);
    const months = Math.floor((daysRemaining % 365) / 30);
    const days = daysRemaining % 30;

    return { years, months, days };
}