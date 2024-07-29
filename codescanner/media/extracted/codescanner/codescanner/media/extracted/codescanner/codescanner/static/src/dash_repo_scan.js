document.addEventListener('DOMContentLoaded', function () {
    // Fetch and display folder structure on page load
    fetch('/folder-data/')
        .then(response => response.json())
        .then(data => {
            displayFolderStructure(data);
        })
        .catch(error => console.error('Error fetching folder data:', error));

    // Function to display the folder structure
    function displayFolderStructure(folders) {
        const container = document.getElementById('folder-structure-custom');
        container.innerHTML = renderFolders(folders);
    }

    // Function to render folders as HTML
    function renderFolders(folders) {
        let html = '<ul>';
        folders.forEach(folder => {
            html += `
                <div class="flex justify-around items-center gap-4 mb-2">
                    <div class="w-3/4">
                        <li class="folder p-2 flex items-center cursor-pointer" data-folder-id="${folder.id}">
                            <svg class="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7a2 2 0 012-2h4l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
                            </svg>
                            ${folder.name}
                        </li>
                    </div>
                    <div class="w-1/4 mt-4">
                        <button class="btn-scan p-2 w-1/3 bg-slate-700  text-white rounded" data-folder-id="${folder.id}">Scan</button>
                    </div>
                </div>`;
        });
        html += '</ul>';
        return html;
    }

    // Event listener for folder structure click actions
    document.getElementById('folder-container-custom').addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-scan')) {
            const folderId = event.target.getAttribute('data-folder-id');
            fetch(`/folder-files/${folderId}/`)
                .then(response => response.json())
                .then(data => {
                    // Handle click action here
                    console.log('Folder ID:', folderId);
                    console.log('Folder Files:', data);
                })
                .catch(error => console.error('Error fetching folder files:', error));
        }
    });

});

// Loader for main section
document.addEventListener("DOMContentLoaded", function() {
    // Simulate loading time
    setTimeout(function() {
        document.getElementById('loader').style.display = 'none';
    }, 2000); // Adjust the timeout duration as needed
});