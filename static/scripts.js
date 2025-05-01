// Add loading state to forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                
                // Re-enable after 10 seconds in case of network issues
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Handle geolocation for nearby page
if (document.getElementById('getLocation')) {
    document.getElementById('getLocation').addEventListener('click', function() {
        if (navigator.geolocation) {
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Getting location...';
            this.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    // Use reverse geocoding to get address from coordinates
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Use a geocoding service like Google Maps or Nominatim
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
                        .then(response => response.json())
                        .then(data => {
                            // Fill in the form fields with the address components
                            const address = data.address;
                            
                            if (document.getElementById('address'))
                                document.getElementById('address').value = address.road || '';
                            
                            if (document.getElementById('city'))
                                document.getElementById('city').value = address.city || address.town || address.village || '';
                            
                            if (document.getElementById('state'))
                                document.getElementById('state').value = address.state || '';
                            
                            if (document.getElementById('zipcode'))
                                document.getElementById('zipcode').value = address.postcode || '';
                            
                            if (document.getElementById('country'))
                                document.getElementById('country').value = address.country || 'USA';
                            
                            document.getElementById('getLocation').innerHTML = 'Use My Location';
                            document.getElementById('getLocation').disabled = false;
                        })
                        .catch(error => {
                            console.error('Error getting address:', error);
                            alert('Error getting address from coordinates. Please enter manually.');
                            document.getElementById('getLocation').innerHTML = 'Use My Location';
                            document.getElementById('getLocation').disabled = false;
                        });
                },
                function(error) {
                    alert('Error getting location: ' + error.message);
                    document.getElementById('getLocation').innerHTML = 'Use My Location';
                    document.getElementById('getLocation').disabled = false;
                }
            );
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    });
}


