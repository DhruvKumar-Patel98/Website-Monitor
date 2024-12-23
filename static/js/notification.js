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

function saveEditForm() {
    try {
        const formData = {
            id: currentCheckId,
            name_of_check: document.getElementById("id_name_of_check").value || "",
            url: document.getElementById("id_url").value || "",
            contact_detail: document.getElementById("id_contact_detail").value || ""
        };
        console.log(formData)

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
            // showSuccessPopupWithCountdown("Updated Successfully!");
            closePopup();
            location.reload();
        })
        .catch(() => alert("Failed to update check. Please try again."));
    } catch {
        alert("An unexpected error occurred. Please check the form and try again.");
    }
}

function closePopup() {
    document.getElementById("editFormPopup").style.display = "none";
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