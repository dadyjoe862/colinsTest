document.addEventListener('DOMContentLoaded', function () {
    const folderSelect = document.getElementById('folder');
    const reportContainer = document.getElementById('report-container');
    const printButton = document.getElementById('print-button');

    if (!folderSelect) {
        console.error("Element with id 'folder' not found.");
        return;
    }

    console.log("DOM fully loaded and parsed");

    // Fetch folders when the page loads
    fetch('/folder_selection_and_report/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log("Fetch response received:", response);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Ensure this is a valid JSON response
    })
    .then(data => {
        console.log("Folders data received:", data);
        populateFolderDropdown(data.folders);
    })
    .catch(error => {
        console.error('Error fetching folders:', error);
    });

    function populateFolderDropdown(folders) {
        folders.forEach(folder => {
            const option = document.createElement('option');
            option.value = folder.id;
            option.textContent = folder.name;
            folderSelect.appendChild(option);
        });
    }

    folderSelect.addEventListener('change', function () {
        const folderId = folderSelect.value;
        console.log("Folder selected:", folderId);

        if (folderId) {
            fetch(`/folder_selection_and_report/?folder=${folderId}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log("Fetch response received:", response);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("Data received:", data);
                renderReport(data.folder_name, data.scan_results);
            })
            .catch(error => {
                console.error('Error fetching report:', error);
                reportContainer.innerHTML = `<p class="text-red-600">Error fetching report: ${error.message}</p>`;
            });
        } else {
            console.log("No folder selected");
            reportContainer.innerHTML = '<p class="text-gray-500">Please select a folder to view the report.</p>';
        }
    });

    function renderReport(folderName, scanResults) {
        console.log("Rendering report for folder:", folderName);
        reportContainer.innerHTML = `
            <h1 class="text-2xl font-bold mb-4">Security Scan Report</h1>
            <h2 class="text-xl font-semibold mb-2">Folder: ${folderName}</h2>
        `;
        try {
            if (!scanResults || scanResults.length === 0) {
                reportContainer.innerHTML += `<p class="text-gray-500">No scan results found.</p>`;
                return;
            }

            reportContainer.innerHTML += generateResultsHTML(scanResults);
            adjustContentWidth();

        } catch (error) {
            console.error('Error rendering report:', error);
            reportContainer.innerHTML = `<p class="text-red-600">Error rendering report: ${error.message}</p>`;
        }
    }

    function generateResultsHTML(scanResults) {
        if (!scanResults || scanResults.length === 0) {
            return `<p class="text-center text-gray-500">No scan results found.</p>`;
        }

        return scanResults.map(result => `
            <div class="mb-6">
                <h2 class="text-xl font-semibold mb-2">File Path: <span class="text-blue-500">${result.file_path}</span></h2>
                <p><strong>Vulnerability Type:</strong> ${result.vulnerability_type}</p>
                <p><strong>Vulnerability Name:</strong> ${result.vulnerability_name}</p>
                <p><strong>Line Number:</strong> ${result.line_number}</p>
                ${wrapCodeSnippet(result.code_snippet)}
                <p><strong>Result:</strong> ${result.result}</p>
                <p><strong>Recommendation:</strong> ${result.recommendation}</p>
                <p><strong>Severity:</strong> ${result.severity}</p>
            </div>
        `).join('');
    }

    function wrapCodeSnippet(code) {
        const maxSnippetLength = 300; // Maximum length to display
        const trimmedCode = code.length > maxSnippetLength ? code.substring(0, maxSnippetLength) + '...' : code;
        return `<pre class="bg-gray-200 p-2 rounded overflow-x-auto"><code class="block whitespace-pre-wrap">${trimmedCode}</code></pre>`;
    }

    function adjustContentWidth() {
        // Select all elements inside reportContainer and set max-width to fit container width
        const elements = reportContainer.querySelectorAll('*');
        elements.forEach(element => {
            element.style.maxWidth = '100%';
            element.style.boxSizing = 'border-box'; // Ensure padding and border are included in width
        });
    }

    printButton.addEventListener('click', function () {
        console.log("Generate PDF button clicked");

        // Fetch folder id from the dropdown
        const folderId = folderSelect.value;

        if (!folderId) {
            console.error("No folder selected");
            alert("Please select a folder to generate PDF.");
            return;
        }

        // Redirect to generate PDF
        window.location.href = `/generate_pdf/?folder=${folderId}`;
    });
});
