from django.contrib import admin
from .models import UploadedFolder, UploadedFile

admin.site.register(UploadedFolder)
admin.site.register(UploadedFile)