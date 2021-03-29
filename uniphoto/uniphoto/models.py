from django.db import models
from django.contrib.auth.models import User


class File(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  file = models.FileField(upload_to='.', default='./none/no-file')
  post_date = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.file.name.split("/")[-1] 
