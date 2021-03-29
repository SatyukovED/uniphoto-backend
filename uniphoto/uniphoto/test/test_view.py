from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.authtoken.models import Token
from uniphoto.models import File
from django.contrib.auth.models import User
from django.conf import settings


NUMBER_NEXT_PAGES_TO_CHECK = 2

  # TODO: Test all views