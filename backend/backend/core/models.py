from django.db import models
import os

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Logic: Keep only the last 5 files
        objects = UploadedFile.objects.all().order_by('-uploaded_at')
        if objects.count() >= 5:
            to_delete = objects[4:] 
            for obj in to_delete:
                if obj.file and os.path.isfile(obj.file.path):
                    os.remove(obj.file.path)
                obj.delete()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"File {self.id}"
