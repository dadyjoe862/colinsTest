document.addEventListener('DOMContentLoaded', function() {
    const foldersContainer = document.getElementById('folders-container');

    // Function to fetch and display folders
    function fetchFolders() {
        fetch('/folder-data/')
            .then(response => response.json())
            .then(data => {
                if (Array.isArray(data)) {
                    data.forEach(folder => {
                        displayFolder(folder);
                    });
                } else {
                    displayFolder(data);
                }
            })
            .catch(error => console.error('Error fetching folder data:', error));
    }

    // Function to display a single folder
    function displayFolder(folder) {
        const folderDiv = document.createElement('div');
        folderDiv.classList.add('bg-white', 'p-4', 'rounded-lg', 'shadow-md', 'flex', 'items-center', 'w-full');

        const folderIcon = document.createElement('div');
        folderIcon.innerHTML = `
            <svg class="w-12 h-12 text-yellow-500 mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h6l2 2h8a2 2 0 012 2v7a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2z"></path>
            </svg>
        `;

        const folderInfo = document.createElement('div');
        folderInfo.innerHTML = `
            <p class="font-semibold text-lg">${folder.name}</p>
            <p class="text-gray-500 text-sm">Path: ${folder.path}</p>
        `;

        const scanButton = document.createElement('button');
        scanButton.textContent = 'Scan Folder';
        scanButton.classList.add('ml-auto', 'bg-blue-500', 'text-white', 'py-2', 'px-4', 'rounded-lg', 'hover:bg-blue-600', 'transition', 'duration-300');
        scanButton.addEventListener('click', () => scanFolder(folder.id, folder.name));

        folderDiv.appendChild(folderIcon);
        folderDiv.appendChild(folderInfo);
        folderDiv.appendChild(scanButton);
        foldersContainer.appendChild(folderDiv);
    }

    // Function to initiate scan
    function scanFolder(folderId, folderName) {
        const scanButton = event.target;
        scanButton.textContent = 'Scanning...';
        scanButton.disabled = true;

        // Fetch file extension for the folder
        fetch(`/folder-files/${folderId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching file extension:', data.error);
                    alert('Failed to initiate scan: File extension not provided.');
                } else {
                    console.log('File extension:', data.file_extension); // Debugging
                    // Call initiateScan with file extension
                    initiateScan(data.file_extension, folderId, folderName);
                }
            })
            .catch(error => {
                console.error('Error fetching file extension:', error);
                alert('Failed to initiate scan: An error occurred while fetching file extension.');
            });
    }

    // Function to initiate scan with file extension
    function initiateScan(fileExtension, folderId, folderName) {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/scan_folder_and_store_results/${folderId}/?file_extension=${fileExtension}`, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    console.log(xhr.responseText);
                    alert(`Scan initiated for folder: ${folderName}. Check results later.`);
                    // Optionally, refresh the folder list or display scan results
                } else {
                    console.error('Scan failed:', xhr.status);
                    alert('Failed to initiate scan.');
                    // Optionally, handle error response
                }
            }
        };
        xhr.send();
    }

    // Initial fetch of folders
    fetchFolders();
});
