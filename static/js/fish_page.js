// Add event listener to search button
document.getElementById("search-button").addEventListener("click", function() {
    // Get search input value
    var searchInput = document.getElementById("search-input").value;
    
    // Make API request to search for fish species
    fetch("/fish-page/search?species_name=" + searchInput)
    .then(response => response.text())
    .then(data => {
        // Display search results
        document.getElementById("search-results").innerHTML = data;
    })
    .catch(error => {
        console.error("Error searching for fish species:", error);
    });
});
