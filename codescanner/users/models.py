import os
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class UploadedFolder(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=1024)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    folder_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

class UploadedFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    folder = models.ForeignKey(UploadedFolder, related_name='files', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return self.name

class ScanResult(models.Model):
    file_path = models.CharField(max_length=1024)
    line_number = models.IntegerField()
    code_snippet = models.TextField()
    result = models.TextField()
    recommendation = models.TextField()
    severity = models.CharField(max_length=50)
    confidence = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_results')
    folder = models.ForeignKey(UploadedFolder, on_delete=models.CASCADE, related_name='scan_results')
    created_at = models.DateTimeField(auto_now_add=True)
    vulnerability_type = models.CharField(max_length=255, blank=True, null=True)
    vulnerability_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Scan Result for {self.file_path} at line {self.line_number}"
