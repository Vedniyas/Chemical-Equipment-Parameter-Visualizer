import os

# 1. Define the paths
base_dir = "core"
models_path = os.path.join(base_dir, "models.py")
serializers_path = os.path.join(base_dir, "serializers.py")
utils_path = os.path.join(base_dir, "utils.py")

# 2. Define the content
models_content = """from django.db import models
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
"""

serializers_content = """from rest_framework import serializers
from .models import UploadedFile

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['file', 'uploaded_at']
"""

utils_content = """import pandas as pd

def process_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Clean column names
        df.columns = [c.strip() for c in df.columns]

        # 1. Total Count
        total_count = len(df)

        # 2. Averages
        stats = {}
        for col in ['Flowrate', 'Pressure', 'Temperature']:
            if col in df.columns:
                stats[f'avg_{col.lower()}'] = round(df[col].mean(), 2)
            else:
                stats[f'avg_{col.lower()}'] = 0

        # 3. Distribution
        if 'Type' in df.columns:
            distribution = df['Type'].value_counts().to_dict()
        else:
            distribution = {}

        return {
            "success": True,
            "total_count": total_count,
            "averages": stats,
            "distribution": distribution,
            "preview": df.head(10).to_dict(orient='records') 
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
"""

# 3. Write the files
print("Writing models.py...")
with open(models_path, "w") as f:
    f.write(models_content)

print("Writing serializers.py...")
with open(serializers_path, "w") as f:
    f.write(serializers_content)

print("Writing utils.py...")
with open(utils_path, "w") as f:
    f.write(utils_content)

print("SUCCESS: All files have been fixed!")