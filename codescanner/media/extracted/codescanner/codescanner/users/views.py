import json
import shutil
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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.http import JsonResponse
# from .models import Files, Folder ,GitHubCredentials
# from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import subprocess
from django.shortcuts import get_object_or_404
import zipfile

# function for scanning files 


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
    print(f"User: {user}")

    folders = UploadedFolder.objects.filter(user=user).values('id', 'name', 'path')
    print(f"Query: UploadedFolder.objects.filter(user={user}).values('id', 'name', 'path')")
    print(f"Folders found: {list(folders)}")
    data = list(folders)

    return JsonResponse(data, safe=False)

@login_required
def folder_files(request, folder_id):
    user = request.user
    print(f"User: {user}, Folder ID: {folder_id}")

    try:
        folder = UploadedFolder.objects.get(id=folder_id, user=user)
        print(f"Folder found: {folder}")
        files = list(folder.files.values('id', 'name', 'file'))
        data = {
            'id': folder.id,
            'name': folder.name,
            'files': files,
        }
    except UploadedFolder.DoesNotExist:
        print(f"Folder does not exist: {folder_id}")
        return JsonResponse({'error': 'Folder does not exist'}, status=404)

    return JsonResponse(data)

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