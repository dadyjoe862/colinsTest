// scan_results.js

// Function to fetch and display scan results
function fetchAndDisplayScanResults() {
    const url = '/path/to/scan_results_json/';

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Filter scan results based on current user's ID
            const currentUserResults = data.files_data.filter(result => result.user_id === currentUserID);

            // Render filtered results on the page
            currentUserResults.forEach(result => {
                const resultElement = createResultElement(result);
                document.getElementById('scan-results-container').appendChild(resultElement);
            });
        })
        .catch(error => {
            console.error('Error fetching scan results:', error);
        });
}

// Function to create a result element for display
function createResultElement(result) {
    const resultElement = document.createElement('div');
    resultElement.textContent = `File: ${result.file_name}, Scan Date: ${result.scan_date}, Scan Result: ${result.scan_result}`;
    return resultElement;
}

// Call the function when the page loads
window.onload = fetchAndDisplayScanResults;
