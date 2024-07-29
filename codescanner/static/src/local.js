function uploadFiles() {
    console.log("Starting folder upload...");

    const input = document.getElementById('fileInput');
    const files = input.files; // Get all selected files
    if (files.length === 0) {
        console.error("No files selected.");
        return;
    }

    console.log("Selected files:", files);

    // Use JSZip to create a zip file from the folder
    const zip = new JSZip();

    // Get the folder name from the first file selected
    const folderName = files[0].webkitRelativePath.split('/')[0];

    // Add files to the zip
    addFilesToZip(zip, files, folderName);

    // Show progress container
    const progressContainer = document.getElementById('progressContainer');
    progressContainer.classList.remove('hidden');

    // Generate the zip file asynchronously
    zip.generateAsync({ type: "blob" }, metadata => {
        // Update progress bar based on total number of files
        const percentComplete = (metadata.percent || 0);
        document.getElementById('uploadProgress').style.width = `${percentComplete}%`;
        document.getElementById('uploadProgress').innerText = `${Math.round(percentComplete)}%`;
    })
    .then(zipBlob => {
        console.log("Generated zip blob:", zipBlob); // Debug statement

        // Create a FormData object and append the zip file
        const formData = new FormData();
        formData.append('zipFile', zipBlob, folderName + '.zip');

        // Retrieve CSRF token from cookie
        const csrftoken = getCookie('csrftoken');
        console.log("CSRF token:", csrftoken);

        // Use XMLHttpRequest to track upload progress
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/uploads/', true);
        xhr.setRequestHeader('X-CSRFToken', csrftoken);

        // Update progress bar and percentage based on individual file upload
        xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
                const percentComplete = ((event.loaded / event.total) * 100 * files.length) / 100;
                document.getElementById('uploadProgress').style.width = `${percentComplete}%`;
                document.getElementById('uploadProgress').innerText = `${Math.round(percentComplete)}%`;
            }
        };

        // Handle response
        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                console.log("Response from Django view:", response);
                showNotification(response.message, 'bg-green-500');
                
                // Add the new folder to the list
                addFolderToList(response.folder_id, response.folder_name);
            } else {
                const response = JSON.parse(xhr.responseText);
                console.error('There was a problem with the upload operation:', xhr.statusText);
                showNotification(response.error || 'Upload failed', 'bg-red-500');
            }
        };

        xhr.onerror = function() {
            console.error('There was a problem with the upload operation:', xhr.statusText);
            showNotification('Upload failed', 'bg-red-500');
        };

        xhr.onloadend = function() {
            // Hide the progress bar after the upload is complete
            progressContainer.classList.add('hidden');
        };

        // Send the form data
        xhr.send(formData);
    });
}

// Function to add files and folders to a JSZip instance
function addFilesToZip(zip, files, folderName) {
    Array.from(files).forEach(file => {
        // Get the relative path of the file
        const relativePath = file.webkitRelativePath || file.name;
        // Remove the folder name from the path
        const filePath = relativePath.substring(relativePath.indexOf('/') + 1);
        // Add the file to the zip with the updated path
        zip.file(folderName + '/' + filePath, file);
    });
}

// Function to display a notification
function showNotification(message, bgColor) {
    const notification = document.createElement('div');
    notification.className = `notification fixed bottom-5 right-5 px-4 py-2 rounded text-white ${bgColor}`;
    notification.innerText = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('hide');
        notification.addEventListener('transitionend', () => {
            notification.remove();
        });
    }, 3000);
}

// Function to retrieve a cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Function to add a folder to the list
function addFolderToList(folderId, folderName) {
    const folderList = document.getElementById('uploadedFolders');
    const folderItem = document.createElement('div');
    folderItem.className = 'bg-white p-4 rounded shadow mb-4';
    folderItem.innerHTML = `<strong>Folder:</strong> ${folderName} <br> <strong>ID:</strong> ${folderId}`;
    folderList.appendChild(folderItem);
}
