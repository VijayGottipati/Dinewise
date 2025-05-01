// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('scripts.js loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const alert = bootstrap.Alert.getOrCreateInstance(message);
            alert.close();
        }, 5000); // Auto-dismiss after 5 seconds
    });
    
    // Handle cuisine selection from the home page
    const cuisineButtons = document.querySelectorAll('.cuisine-btn');
    cuisineButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const cuisine = this.getAttribute('data-cuisine');
            selectCuisine(cuisine);
        });
    });
});

// Function to handle cuisine selection from the home page
function selectCuisine(cuisine) {
    console.log("Selected cuisine:", cuisine);
    // Get the search form
    const searchForm = document.getElementById('searchForm');
    if (!searchForm) return;
    
    // Set the cuisine in the form
    const cuisineInput = document.getElementById('cuisine');
    if (cuisineInput) {
        cuisineInput.value = cuisine;
    }
    
    // If location is empty, try to get a default
    const locationInput = document.getElementById('location');
    if (locationInput && !locationInput.value) {
        locationInput.value = 'San Francisco, CA';
    }
    
    // Submit the form
    searchForm.submit();
}

// Handle geolocation for nearby page
if (document.getElementById('getLocation')) {
    document.getElementById('getLocation').addEventListener('click', function() {
        if (navigator.geolocation) {
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Getting location...';
            this.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    // Success handler
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Use reverse geocoding to get location name
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
                        .then(response => response.json())
                        .then(data => {
                            let location = '';
                            if (data && data.address) {
                                const city = data.address.city || data.address.town || data.address.village;
                                const state = data.address.state;
                                if (city && state) {
                                    location = `${city}, ${state}`;
                                }
                            }
                            
                            const locationInput = document.getElementById('location');
                            if (locationInput) {
                                locationInput.value = location || `${lat},${lng}`;
                                locationInput.form.submit();
                            }
                        })
                        .catch(error => {
                            console.error("Error with geocoding:", error);
                            const locationInput = document.getElementById('location');
                            if (locationInput) {
                                locationInput.value = `${lat},${lng}`;
                                locationInput.form.submit();
                            }
                        });
                },
                function(error) {
                    // Error handler
                    console.error("Geolocation error:", error);
                    alert("Could not get your location. Please enter it manually.");
                    
                    const locationButton = document.getElementById('getLocation');
                    if (locationButton) {
                        locationButton.innerHTML = '<i class="fas fa-map-marker-alt me-1"></i>Use My Location';
                        locationButton.disabled = false;
                    }
                },
                {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                }
            );
        } else {
            alert("Geolocation is not supported by your browser. Please enter your location manually.");
        }
    });
}
