from django.core.exceptions import ValidationError
import os


def validate_file_extension(value):
  ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
  valid_extensions = ['.jpg', '.jpeg', '.mp4']
  if not ext.lower() in valid_extensions:
    raise ValidationError('Unsupported file extension. Supported file extensions: .jpg, .jpeg, .mp4')