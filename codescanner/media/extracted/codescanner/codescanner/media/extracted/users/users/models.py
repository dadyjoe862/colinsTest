import uuid
from django.contrib.auth.models import User
from django.db import models

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
    result = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_results')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan Result for {self.file_path}"