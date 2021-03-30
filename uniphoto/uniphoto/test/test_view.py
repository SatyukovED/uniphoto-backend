from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.authtoken.models import Token
from uniphoto.models import File
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import json


NUMBER_NEXT_PAGES_TO_CHECK = 2


"""
  TODO:
  Test
    - UserFilesListView
    - AllFilesListView
    - PostFileView
    - DeleteFileView 
"""


class UserDetailsViewTests(APITestCase):

  def test_get_user_details_with_valid_token(self):
    """
    Test attempt to get user details with valid token.
    """
    # test user
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=user)
    # url for request        
    url = '/user-details'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, {'email': 'azalia@uniphoto.com', 'username': 'azalia'})

  def test_get_user_details_with_invalid_token(self):
    """
    Test attempt to get user details with inavlid token.
    """
    # mannually add invalid credentials to all requests from client 
    self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_token'))
    # url for request        
    url = '/user-details'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

  def test_get_user_details_without_token_header(self):
    """
    Test attempt to get user details without token header.
    """
    # url for request        
    url = '/user-details'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})


class TrialLicenseCheckViewTests(APITestCase):
  
  def test_check_trial_license_with_valid_token(self):
    """
    Test attempt to check trial license with valid token.
    """
    # test user
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)
    
    # calculate days to license end with default license duration (= 30)
    datetime_now = timezone.now()
    datetime_joined = test_user.date_joined 
    license_duration = 30
    days_to_license_end =  license_duration - (datetime_now - datetime_joined).days
    if days_to_license_end < 0:
      days_to_license_end = 0

    # url for request        
    url = '/trial-license-check'
    # get request to url 
    response = self.client.generic(method='GET', path=url, content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['days_to_license_end'], days_to_license_end)

    # calculate days to license end with non default license duration (!= 30)
    license_duration = 15
    days_to_license_end =  license_duration - (datetime_now - datetime_joined).days
    if days_to_license_end < 0:
      days_to_license_end = 0

    # data for request
    data = {'license_duration': 15}
    # get request to url with data in json format
    response = self.client.generic(method='GET', path=url, data=json.dumps(data), content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['days_to_license_end'], days_to_license_end)

  def test_check_trial_license_with_invalid_token(self):
    """
    Test attempt to check trial license with inavlid token.
    """
    # mannually add invalid credentials to all requests from client 
    self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_token'))
    # url for request        
    url = '/trial-license-check'
    # get request to url 
    response = self.client.generic(method='GET', path=url, content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

  def test_check_trial_license_without_token_header(self):
    """
    Test attempt to check trial license without token header.
    """
    # url for request        
    url = '/trial-license-check'
    # get request to url 
    response = self.client.generic(method='GET', path=url, content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})
