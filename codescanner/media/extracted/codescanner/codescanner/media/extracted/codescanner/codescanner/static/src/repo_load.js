document.addEventListener('DOMContentLoaded', function () {
    fetch('/folder-data/')
        .then(response => response.json())
        .then(data => {
            displayFolderStructure(data);
        })
        .catch(error => console.error('Error fetching folder data:', error));

    function displayFolderStructure(folders) {
        const container = document.getElementById('folder-structure');
        container.innerHTML = renderFolders(folders);
    }

    function renderFolders(folders) {
        let html = '<ul>';
        folders.forEach(folder => {
            html += `
            <div class="flex justify-evenly items-center gap-4" data-id="${folder.id}">
                <div class="w-3/4">
                    <li class="folder p-2 flex items-center" data-id="${folder.id}">
                        <svg class="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7a2 2 0 012-2h4l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
                        </svg>
                        ${folder.name}
                    </li>
                </div>
                <div>
                    <a href="javascript:void(0)" class="text-red-700 btn-delete" data-id="${folder.id}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-folder-x" viewBox="0 0 16 16">
                        <path d="M.54 3.87.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3h3.982a2 2 0 0 1 1.992 2.181L15.546 8H14.54l.265-2.91A1 1 0 0 0 13.81 4H2.19a1 1 0 0 0-.996 1.09l.637 7a1 1 0 0 0 .995.91H9v1H2.826a2 2 0 0 1-1.991-1.819l-.637-7a2 2 0 0 1 .342-1.31zm6.339-1.577A1 1 0 0 0 6.172 2H2.5a1 1 0 0 0-1 .981l.006.139q.323-.119.684-.12h5.396z"/>
                        <path d="M11.854 10.146a.5.5 0 0 0-.707.708L12.293 12l-1.146 1.146a.5.5 0 0 0 .707.708L13 12.707l1.146 1.147a.5.5 0 0 0 .708-.708L13.707 12l1.147-1.146a.5.5 0 0 0-.707-.708L13 11.293z"/>
                        </svg>
                    </a>
                </div>
            </div>`;
        });
        html += '</ul>';
        return html;
    }

    document.getElementById('folder-structure').addEventListener('click', function(event) {
        const folderElement = event.target.closest('.folder');
        if (folderElement) {
            const folderId = folderElement.getAttribute('data-id');
            console.log(`Folder clicked: ${folderId}`);  // Debug statement
            fetch(`/folder-files/${folderId}/`)
                .then(response => response.json())
                .then(data => {
                    console.log('Fetched folder files:', data);  // Debug statement
                    highlightSelectedFolder(folderElement);
                    displayFiles(data);
                })
                .catch(error => console.error('Error fetching folder files:', error));
        } else if (event.target.closest('.btn-scan')) {
            const folderId = event.target.closest('.btn-scan').getAttribute('data-id');
            console.log(`Scanning folder ${folderId}`);
            // Add your scanning logic here
        } else if (event.target.closest('.btn-delete')) {
            const folderId = event.target.closest('.btn-delete').getAttribute('data-id');
            console.log(`Deleting folder ${folderId}`);
            deleteFolder(folderId);
        }
    });

    function highlightSelectedFolder(selectedFolder) {
        const folders = document.querySelectorAll('.folder');
        folders.forEach(folder => {
            folder.classList.remove('highlight');
        });
        selectedFolder.classList.add('highlight');
        console.log(`Highlighted folder: ${selectedFolder.getAttribute('data-id')}`);  // Debug statement
    }

    function displayFiles(folder) {
        const container = document.getElementById('file-list');
        const title = document.getElementById('file-list-title');
        if (title) {
            title.textContent = `Files in ${folder.name}`;
        }
        let html = '<ul>';
        folder.files.forEach((file, index) => {
            html += `<li class="p-2 border-b border-gray-200 flex gap-2">
                ${index + 1}.
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-code" viewBox="0 0 16 16">
                    <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5z"/>
                    <path d="M8.646 6.646a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1 0 .708l-2 2a.5.5 0 0 1-.708-.708L10.293 9 8.646 7.354a.5.5 0 0 1 0-.708m-1.292 0a.5.5 0 0 0-.708 0l-2 2a.5.5 0 0 0 0 .708l2 2a.5.5 0 0 0 .708-.708L5.707 9l1.647-1.646a.5.5 0 0 0 0-.708"/>
                  </svg>
                ${file.name}</li>`;
        });
        html += '</ul>';
        container.innerHTML = html;
        console.log('Displayed files for folder:', folder.name);  // Debug statement
    }

    function deleteFolder(folderId) {
        fetch(`/delete-folder/${folderId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                console.log(data.message);
                document.querySelector(`div[data-id="${folderId}"]`).remove();
            } else {
                console.error(data.error);
            }
        })
        .catch(error => console.error('Error deleting folder:', error));
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
});

// Loader for main section
document.addEventListener("DOMContentLoaded", function() {
    // Simulate loading time
    setTimeout(function() {
        document.getElementById('loader').style.display = 'none';
    }, 1000); // Adjust the timeout duration as needed
});
