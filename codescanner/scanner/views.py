from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from users.models import UploadedFolder, ScanResult
import os

@login_required
def scan_folder_and_store_results(request, folder_id):
    user = request.user
    print(f"Scanning folder for user: {user}, Folder ID: {folder_id}")  # Debugging statement
    try:
        folder = UploadedFolder.objects.get(id=folder_id, user=user)
        print(f"Folder found: {folder}")  # Debugging statement
        files = folder.files.all()
        vulnerabilities_found = []

        for file in files:
            file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
            print(f"Scanning file: {file_path}")  # Debugging statement
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                # Hypothetical scanning function that returns vulnerabilities
                vulnerabilities = scan_file(content)
                for vulnerability in vulnerabilities:
                    ScanResult.objects.create(
                        file_path=file_path,
                        line_number=vulnerability['line_number'],
                        code_snippet=vulnerability['code_snippet'],
                        result=vulnerability['result'],
                        recommendation=vulnerability['recommendation'],
                        user=user
                    )
                    vulnerabilities_found.append(vulnerability)
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'vulnerabilities_found': vulnerabilities_found})
    except UploadedFolder.DoesNotExist:
        print(f"Folder does not exist for user: {user}, Folder ID: {folder_id}")  # Debugging statement
        return JsonResponse({'error': 'Folder does not exist'}, status=404)

# Placeholder scan_file function
def scan_file(file_content):
    """
    Placeholder function for scanning a file content. 
    This should contain the logic to analyze the file content.
    """
    scan_results = []
    # Add some debugging statements
    print("Scanning file content...")
    # Example condition to demonstrate scanning
    if 'TODO' in file_content:
        scan_results.append({
            'line_number': 1,
            'code_snippet': 'TODO: Example',
            'result': 'TODO found',
            'recommendation': 'Consider completing this TODO',
            'severity': 'Medium',  # Example severity
            'confidence': 'High'  # Example confidence
        })
    return scan_results

@login_required
def display_scan_results(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be logged in to view this page.", status=401)
    
    # Fetch scan results for the logged-in user
    scan_results = ScanResult.objects.filter(user=request.user)
    
    # Debugging statement
    print(f"Fetched {scan_results.count()} scan results for user: {request.user.username}")
    
    return render(request, 'scanner/scan_result.html', {'scan_results': scan_results})
