console.log("Featured.js loaded at", new Date().toISOString());

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, featured.js running");
    
    // Default location if user doesn't share location
    const defaultLocation = 'San Francisco, CA';
    
    // Function to fetch featured restaurants
    function fetchFeaturedRestaurants(location) {
        console.log("Fetching featured restaurants for:", location);
        const featuredContainer = document.getElementById('featured-restaurants');
        
        if (!featuredContainer) {
            console.error("Featured container not found");
            return;
        }
        
        // Show loading spinner
        featuredContainer.innerHTML = `
            <div class="col-12 text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading featured restaurants...</p>
            </div>
        `;
        
        // First check if API is working
        fetch('/api/test')
            .then(response => response.json())
            .then(testData => {
                console.log("API test response:", testData);
                
                if (!testData.yelp_api_key_configured) {
                    throw new Error("Yelp API key not configured on server");
                }
                
                // Now fetch the actual featured restaurants
                return fetch(`/api/featured?location=${encodeURIComponent(location)}`);
            })
            .then(response => {
                console.log("API response status:", response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        console.error("API error response:", text);
                        throw new Error(`API error: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("Featured data received:", data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Clear container
                featuredContainer.innerHTML = '';
                
                // Check if we have results
                if (!data.restaurants || data.restaurants.length === 0) {
                    featuredContainer.innerHTML = '<div class="col-12 text-center"><p>No featured restaurants found.</p></div>';
                    return;
                }
                
                // Add each restaurant to the container
                data.restaurants.forEach(restaurant => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 mb-4';
                    
                    const imageUrl = restaurant.image_url || '/static/img/no-image.jpg';
                    const rating = restaurant.rating || 'N/A';
                    const reviewCount = restaurant.review_count || 0;
                    const categories = restaurant.categories ? restaurant.categories.map(c => c.title).join(', ') : '';
                    
                    col.innerHTML = `
                        <div class="card h-100 shadow-sm">
                            <img src="${imageUrl}" class="card-img-top restaurant-img" alt="${restaurant.name}" style="height: 200px; object-fit: cover;">
                            <div class="card-body">
                                <h5 class="card-title">${restaurant.name}</h5>
                                <p class="card-text">
                                    <small class="text-muted">
                                        <i class="fas fa-star text-warning"></i> ${rating} (${reviewCount} reviews)
                                    </small>
                                </p>
                                <p class="card-text">${categories}</p>
                            </div>
                            <div class="card-footer bg-transparent">
                                <a href="/restaurant/${restaurant.id}" class="btn btn-outline-primary w-100">
                                    <i class="fas fa-info-circle me-1"></i>View Details
                                </a>
                            </div>
                        </div>
                    `;
                    
                    featuredContainer.appendChild(col);
                });
            })
            .catch(error => {
                console.error('Error fetching featured restaurants:', error);
                featuredContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <div class="alert alert-warning" role="alert">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error loading featured restaurants: ${error.message}
                            <hr>
                            <p class="mb-0">Please check your API configuration and try again later.</p>
                        </div>
                    </div>
                `;
            });
    }
    
    // Function to initialize featured section
    function initFeatured() {
        console.log("Initializing featured section");
        
        // Check if we're on the home page and the featured section exists
        const featuredContainer = document.getElementById('featured-restaurants');
        if (!featuredContainer) {
            console.log("Not on home page or featured container not found");
            return;
        }
        
        // Use default location immediately to avoid delay
        fetchFeaturedRestaurants(defaultLocation);
        
        // Try to get user's location in the background
        if (navigator.geolocation) {
            console.log("Requesting user location");
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    console.log("Got user position:", position.coords);
                    // Use reverse geocoding to get location name
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log("Geocoding response:", data);
                            let location = defaultLocation;
                            if (data && data.address) {
                                const city = data.address.city || data.address.town || data.address.village;
                                const state = data.address.state;
                                if (city && state) {
                                    location = `${city}, ${state}`;
                                    // Only fetch again if location is different
                                    if (location !== defaultLocation) {
                                        fetchFeaturedRestaurants(location);
                                    }
                                }
                            }
                        })
                        .catch(error => {
                            console.error("Error with geocoding:", error);
                        });
                },
                function(error) {
                    console.error("Geolocation error:", error);
                },
                {timeout: 5000} // Set a timeout of 5 seconds
            );
        }
    }
    
    // Start the process
    initFeatured();
});



