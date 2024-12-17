    function filterCountries() {
        const input = document.getElementById('searchLocation');
        const filter = input.value.toLowerCase();
        const options = document.querySelectorAll('.country-option');
        
        options.forEach(option => {
            const label = option.querySelector('label').innerText.toLowerCase();
            option.style.display = label.includes(filter) ? '' : 'none';
        });
    }

    document.getElementById('toggleForm').addEventListener('click', function() {
        var formContainer = document.getElementById('formContainer');
        var arrow = document.getElementById('arrow');

        if (formContainer.style.display === 'none' || formContainer.style.display === '') {
            formContainer.style.display = 'block';
            arrow.innerHTML = '&#x25B2;';
        } else {
            formContainer.style.display = 'none';
            arrow.innerHTML = '&#x25BC;'; 
        }
    });

    function updateSlider(slider) {
        const value = slider.value;
        const min = slider.min ? slider.min : 0;
        const max = slider.max ? slider.max : 100;
        const percentage = (value - min) / (max - min) * 100;

        slider.style.background = `linear-gradient(to right, lightblue ${percentage}%, #ccc ${percentage}%)`;
        slider.nextElementSibling.value = value; // Update the output value
    }

    const toggle = document.getElementById("default_port_toggle");
    const customPortContainer = document.getElementById("custom_port_container");

    toggle.addEventListener("change", function () {
        if (this.checked) {
            customPortContainer.classList.remove("visible-inline");
            customPortContainer.classList.add("hidden-inline");
        } else {
            customPortContainer.classList.remove("hidden-inline");
            customPortContainer.classList.add("visible-inline");
        }
    });