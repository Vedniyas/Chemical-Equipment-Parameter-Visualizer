
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Import the views from our 'core' app
from core.views import UploadAndProcessView, HistoryView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/upload/', UploadAndProcessView.as_view(), name='file-upload'),
    path('api/history/', HistoryView.as_view(), name='file-history'),
]

# Allow serving media files (CSVs) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
