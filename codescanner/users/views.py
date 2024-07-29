from collections import defaultdict
import json
# import chardet
import shutil
from django.utils import timezone
from venv import logger
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from .models import ScanResult, UploadedFile, UploadedFolder
from .forms import createUserForm
import os
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.http import JsonResponse
# from .models import Files, Folder ,GitHubCredentials
# from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import subprocess
from django.shortcuts import get_object_or_404
import zipfile
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.db.models import Count

logger = logging.getLogger(__name__)


def vulnerability_chart(request):
    # Retrieve ScanResult objects
    scan_results = ScanResult.objects.all()

    # Analyze and categorize vulnerabilities
    vulnerabilities = {
        'SQL Injection': 0,
        'XSS': 0,
        'Other': 0  # You can add more vulnerability types here
    }

    for result in scan_results:
        if 'sql injection' in result.result.lower():
            vulnerabilities['SQL Injection'] += 1
        elif 'xss' in result.result.lower():
            vulnerabilities['XSS'] += 1
        else:
            vulnerabilities['Other'] += 1

    # Prepare data for Chart.js
    labels = list(vulnerabilities.keys())
    data = list(vulnerabilities.values())

    # Create a Chart.js compatible data structure
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Vulnerabilities',
            'backgroundColor': ['#ff6384', '#36a2eb', '#ffce56'],  # Colors for each bar
            'data': data,
        }]
    }

    # Convert chart data to JSON
    chart_data_json = json.dumps(chart_data)

    return render(request, 'vulnerability_chart.html', {'chart_data_json': chart_data_json})


@login_required
def code_analysis(request):
   
    return render(request, "users/code_analysis.html")

@login_required
def generate_pdf(request):
    folder_id = request.GET.get('folder')
    if not folder_id:
        return HttpResponse(status=400, content='Folder ID not provided')

    scan_results = ScanResult.objects.filter(folder_id=folder_id)

    buffer = io.BytesIO()

    # Create a canvas
    c = canvas.Canvas(buffer, pagesize=letter)

    # PDF Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "Scan Results")

    # Add scan results to PDF
    y_position = 700  # Initial y position
    for result in scan_results:
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"File Path: {result.file_path}")
        c.drawString(50, y_position - 20, f"Line Number: {result.line_number}")
        c.drawString(50, y_position - 40, f"Severity: {result.severity}")
        c.drawString(50, y_position - 60, f"Confidence: {result.confidence}")
        c.drawString(50, y_position - 80, f"Result: {result.result}")
        c.drawString(50, y_position - 100, f"Recommendation: {result.recommendation}")

        # Move to the next block
        y_position -= 140  # Adjust this value based on your content

        # Check if new page needed
        if y_position < 100:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(300, 750, "Scan Results")
            y_position = 700

    c.save()

    # Get the value of the BytesIO buffer and return response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="scan_results.pdf"'
    return response

@login_required
def report(request):
    return render(request, "users/scan_report.html")

def folder_selection_and_report(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        folder_id = request.GET.get('folder')
        
        if folder_id:
            folder = get_object_or_404(UploadedFolder, id=folder_id)
            scan_results = ScanResult.objects.filter(folder=folder)
            
            # Prepare data in a format expected by the frontend
            scan_results_data = []
            for result in scan_results:
                scan_results_data.append({
                    'file_path': result.file_path,
                    'line_number': result.line_number,
                    'code_snippet': result.code_snippet,
                    'result': result.result,
                    'recommendation': result.recommendation,
                    'severity': result.severity,
                    'vulnerability_type': result.vulnerability_type,
                    'vulnerability_name': result.vulnerability_name,
                })
            
            # Return JSON response with scan results data
            return JsonResponse({
                'folder_name': folder.name,
                'scan_results': scan_results_data
            })
        else:
            folders = UploadedFolder.objects.all()
            folders_data = [{"id": folder.id, "name": folder.name} for folder in folders]
            return JsonResponse({"folders": folders_data})

    # If not an AJAX request, render the scan_results.html template
    folders = UploadedFolder.objects.all()
    return render(request, 'users/scan_results.html', {'folders': folders})



@login_required
def scan_folder_and_store_results(request, folder_id):
    user = request.user
    file_extension = request.GET.get('file_extension')

    if not file_extension:
        return JsonResponse({'error': 'File extension not provided'}, status=400)

    try:
        folder = get_object_or_404(UploadedFolder, id=folder_id, user=user)
        files = folder.files.all()
        vulnerabilities_found = []  # Initialize vulnerabilities_found list

        for file in files:
            file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)

            if file_path.endswith('.pyc'):
                continue  # Skip .pyc files and other binary files

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                vulnerabilities = scan_file(content, file_extension)

                for vulnerability in vulnerabilities:
                    required_keys = ['line_number', 'code_snippet', 'result', 'recommendation', 'severity', 'confidence', 'vulnerability_type', 'vulnerability_name']
                    if all(key in vulnerability for key in required_keys):
                        scan_result = ScanResult.objects.create(
                            file_path=file_path,
                            line_number=vulnerability['line_number'],
                            code_snippet=vulnerability['code_snippet'],
                            result=vulnerability['result'],
                            recommendation=vulnerability['recommendation'],
                            severity=vulnerability['severity'],
                            confidence=vulnerability['confidence'],
                            vulnerability_type=vulnerability['vulnerability_type'],
                            vulnerability_name=vulnerability['vulnerability_name'],
                            folder=folder,
                            user=user,
                            created_at=timezone.now()
                        )
                        print(f"Created ScanResult: {scan_result}")
                        vulnerabilities_found.append(vulnerability)  # Append to vulnerabilities_found list
                    else:
                        print(f"Vulnerability data missing keys: {vulnerability}")
                        return JsonResponse({'error': 'Vulnerability data missing keys'}, status=500)

            except FileNotFoundError:
                return HttpResponseNotFound("File not found")
            except Exception as e:
                print(f"Error scanning file: {file_path}, Error: {e}")
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'vulnerabilities_found': vulnerabilities_found})

    except UploadedFolder.DoesNotExist:
        print(f"Folder does not exist for user: {user}, Folder ID: {folder_id}")
        return JsonResponse({'error': 'Folder does not exist'}, status=404)


# Placeholder scan_file function
def scan_file(content, file_extension):
    """
    Scan the content of a file for vulnerabilities based on its language.
    """
    if file_extension.lower() == '.py':
        from .python_scanner import scan_python_code
        return scan_python_code(content)
    elif file_extension.lower() == '.php':
        from .php_scanner import scan_php_code
        return scan_php_code(content)
    elif file_extension.lower() == '.html':
        from .html_scanner import scan_html_code
        return scan_html_code(content)
    elif file_extension.lower() == '.js':
        from .js_scanner import scan_javascript_code
        return scan_javascript_code(content)
    else:
        return []



# Function to display scan results
@login_required
def display_scan_results(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be logged in to view this page.", status=401)
    
    # Fetch scan results for the logged-in user
    scan_results = ScanResult.objects.filter(user=request.user)
    
    # Debugging statement
    print(f"Fetched {scan_results.count()} scan results for user: {request.user.username}")
    
    return render(request, 'users/scan_result.html', {'scan_results': scan_results})




# repository view function 
def repos(request):
    return render(request, "users/repositories.html")

# deletion folder function 
def delete_folder_view(request, folder_id):
    # Ensure this view is accessible only via DELETE
    if request.method == 'DELETE':
        try:
            folder = get_object_or_404(UploadedFolder, id=folder_id)
            folder_path = folder.path

            # Delete associated files from the database
            UploadedFile.objects.filter(folder=folder).delete()

            # Delete the folder from the database
            folder.delete()

            # Remove the folder and its content from the file system
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            return JsonResponse({'message': 'Folder and its files deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# open files content function 
def file_content_view(request, file_id):
    # Ensure this view is accessible only via GET
    if request.method == 'GET':
        # Fetch the file from the database using its ID
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return JsonResponse({'content': content})
        except FileNotFoundError:
            return HttpResponseNotFound("File not found")
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def folder_data(request):
    user = request.user
    folder_id = request.GET.get('folder_id')  # Get the folder_id from the query parameters

    if folder_id is not None:
        try:
            folder_id = int(folder_id)
            folder = get_object_or_404(UploadedFolder, id=folder_id, user=user)
            data = {
                'id': folder.id,
                'name': folder.name,
                'path': folder.path,
            }
            logger.info(f"Folder found: {data}")
            return JsonResponse(data)
        except ValueError:
            logger.error(f"Invalid folder_id: {folder_id}")
            return HttpResponseBadRequest("Invalid folder_id")
        except UploadedFolder.DoesNotExist:
            logger.error(f"Folder does not exist: {folder_id}")
            return JsonResponse({'error': 'Folder does not exist'}, status=404)
    else:
        # If no folder_id is provided, return all folders for the user
        folders = UploadedFolder.objects.filter(user=user).values('id', 'name', 'path')
        logger.info(f"Folders found: {list(folders)}")
        data = list(folders)
        return JsonResponse(data, safe=False)

@login_required
def folder_files(request, folder_id):
    user = request.user
    print(f"User: {user}, Folder ID: {folder_id}")

    try:
        folder = UploadedFolder.objects.get(id=folder_id, user=user)
        print(f"Folder found: {folder}")

        # Get file extension for the folder
        file_extension = get_folder_file_extension(folder)
        print(f"File extension: {file_extension}")

        files = list(folder.files.values('id', 'name', 'file'))
        data = {
            'id': folder.id,
            'name': folder.name,
            'files': files,
            'file_extension': file_extension,
        }
        return JsonResponse(data)
    except UploadedFolder.DoesNotExist:
        print(f"Folder does not exist: {folder_id}")
        return JsonResponse({'error': 'Folder does not exist'}, status=404)
    except Exception as e:
        print(f"Error fetching folder files: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    


def get_folder_file_extension(folder):
    try:
        # Get all files in the folder
        files = folder.files.all()

        # Count occurrences of each file extension
        extension_counts = {}
        for file in files:
            _, extension = os.path.splitext(file.name)
            extension = extension.lower()  # Normalize extension to lowercase
            extension_counts[extension] = extension_counts.get(extension, 0) + 1

        # Sort extensions by count in descending order
        sorted_extensions = sorted(extension_counts.items(), key=lambda x: x[1], reverse=True)

        # Get the most common extension
        if sorted_extensions:
            most_common_extension = sorted_extensions[0][0]
            return most_common_extension
        else:
            # If no files found, return a default extension
            return '.txt'  # Default to txt extension if no files found
    except Exception as e:
        print(f"Error getting folder file extension: {e}")
        return '.txt'  # Return a default extension in case of error

@login_required
def folder(request):
    print(f"Rendering folder view for user: {request.user}")
    return render(request, 'users/dashboard.html')

@login_required
def upload_view(request):
    if request.method == 'POST':
        if 'zipFile' in request.FILES:
            uploaded_file = request.FILES['zipFile']
            user = request.user
            print(f"Uploaded file: {uploaded_file} by user: {user}")

            # Save the uploaded ZIP file temporarily
            temp_zip_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            with open(temp_zip_path, 'wb+') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            # Extract the ZIP file
            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    # Extract to a unique directory to avoid name conflicts
                    extracted_folder_name = uploaded_file.name.split('.')[0]
                    extracted_path = os.path.join(settings.MEDIA_ROOT, 'extracted', extracted_folder_name)
                    zip_ref.extractall(extracted_path)
                    print(f"Extracted folder: {extracted_folder_name} to path: {extracted_path}")

                    # Save the extracted folder to the database
                    uploaded_folder = UploadedFolder.objects.create(
                        name=extracted_folder_name,
                        path=extracted_path,
                        user=user  # Associate with the authenticated user
                    )
                    print(f"Uploaded folder saved: {uploaded_folder} for user: {user}")

                    # Save the extracted files to the database, preserving directory structure
                    for root, dirs, files in os.walk(extracted_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                            relative_path_in_zip = os.path.relpath(file_path, extracted_path)
                            uploaded_file = UploadedFile.objects.create(
                                name=relative_path_in_zip,
                                file=relative_path,
                                folder=uploaded_folder,
                                user=user  # Associate with the authenticated user
                            )
                            print(f"Uploaded file saved: {uploaded_file}")

                # Cleanup the temporary ZIP file
                os.remove(temp_zip_path)
                print(f"Temporary zip file removed: {temp_zip_path}")

                response_data = {
                    'message': 'File uploaded and extracted successfully!',
                    'folder_id': uploaded_folder.id,
                    'folder_name': uploaded_folder.name
                }
                return JsonResponse(response_data)
            except zipfile.BadZipFile:
                print(f"Invalid ZIP file: {uploaded_file}")
                return JsonResponse({'error': 'Invalid ZIP file'}, status=400)
        else:
            print("No file uploaded")
            return JsonResponse({'error': 'No file uploaded'}, status=400)
    else:
        print(f"Invalid request method: {request.method}")
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# Views for managing GitHub integration




# User authentication and management views

@never_cache
def register(request):
    form = createUserForm()
    if request.method == 'POST':
        form = createUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            return redirect('users-login') 
    context = {'registerForm': form}
    return render(request, 'users/register.html', context=context)

@never_cache
def loginForm(request):
    if request.user.is_authenticated:
        return redirect('users-dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('users-dashboard')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('users-login')
    return render(request, 'users/login.html')

def logoutUser(request):
    logout(request)
    return redirect('users-login')

@login_required(login_url='users-login')
@never_cache
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'users/dashboard.html')
    else:
        return render(request, 'users/login.html')

@login_required(login_url='users-login')
@never_cache
def scan(request):
    if request.user.is_authenticated:
        return render(request, 'users/scan_result.html')
    else:
        return render(request, 'users/login')

@login_required(login_url='users-login')
@never_cache
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'users/profile.html')
    else:
        return render(request, 'users/login.html')