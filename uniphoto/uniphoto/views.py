from rest_framework import generics, permissions 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
import os
from .models import File
from .serializers import UserSerializer, TrialLicenseCheckSerializer, UserFilesSerializer, AllFilesSerializer


class UserRegistration(generics.CreateAPIView):
  permission_classes = [permissions.AllowAny]
  queryset = User.objects.all()
  serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    return Response({'email': self.request.user.email, 'username': self.request.user.username})

class TrialLicenseCheck(generics.RetrieveAPIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    datetime_now = timezone.now()
    datetime_joined = request.user.date_joined 
    license_duration = TrialLicenseCheckSerializer(request.data).data['license_duration']
    days_to_license_end =  license_duration - (datetime_now - datetime_joined).days
    if days_to_license_end < 0:
      days_to_license_end = 0
    return Response({'days_to_license_end': days_to_license_end})

class UserFilesList(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = UserFilesSerializer

  def get_queryset(self, *args, **kwargs):
    return File.objects.all().filter(user=self.request.user).order_by(F('id').desc())

class AllFilesList(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = AllFilesSerializer

  def get_queryset(self, *args, **kwargs):
    return File.objects.all().annotate(username=F('user__username')).order_by(F('id').desc())

class PostFile(generics.CreateAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = UserFilesSerializer

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

class DeleteFile(generics.DestroyAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = UserFilesSerializer

  def delete(self, request, pk):
    file = get_object_or_404(File, id=pk)
    if request.user == file.user:
      file.delete()
      os.remove(file.file.path)
      return Response({'message': 'File was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT) 
    else:
      return Response({'message': 'You cannot delete files of other users.'}, status=status.HTTP_403_FORBIDDEN) 
