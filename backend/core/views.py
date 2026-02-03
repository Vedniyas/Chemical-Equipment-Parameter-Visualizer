from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadedFile
from .serializers import FileUploadSerializer
from .utils import process_csv_data

class UploadAndProcessView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileUploadSerializer(data=request.data)
        
        if file_serializer.is_valid():
            # 1. Save file to DB (History)
            file_instance = file_serializer.save()
            
            # 2. Process with Pandas
            # We pass the file path to our utility function
            analysis_result = process_csv_data(file_instance.file.path)
            
            if analysis_result['success']:
                return Response({
                    "message": "File processed successfully",
                    "file_id": file_instance.id,
                    "data": analysis_result
                }, status=200)
            else:
                return Response({
                    "message": "Error processing CSV",
                    "error": analysis_result['error']
                }, status=400)
        
        return Response(file_serializer.errors, status=400)

class HistoryView(APIView):
    def get(self, request):
        # Return last 5 uploads
        files = UploadedFile.objects.all().order_by('-uploaded_at')[:5]
        serializer = FileUploadSerializer(files, many=True)
        return Response(serializer.data)