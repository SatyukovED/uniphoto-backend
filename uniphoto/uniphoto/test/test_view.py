from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import math
import json
import os
from uniphoto.models import File


NUMBER_NEXT_PAGES_TO_CHECK = 2


"""
  TODO:
  Test
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
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)
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
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username='nastya')
    self.client.force_authenticate(user=test_user)

    # calculate days to license
    datetime_now = timezone.now()
    datetime_joined = test_user.date_joined 
    license_duration = 30
    days_to_license_end =  license_duration - (datetime_now - datetime_joined).days

    # url for request        
    url = '/trial-license-check'
    # get request to url 
    response = self.client.generic(method='GET', path=url, content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['days_to_license_end'], days_to_license_end)

  def test_check_trial_license_with_non_default_license_duration(self):
    """
    Test attempt to check trial license with non default license duration (!= 30 days).
    """
    # test user
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username='nastya')
    self.client.force_authenticate(user=test_user)

    # calculate days to license end
    datetime_now = timezone.now()
    datetime_joined = test_user.date_joined 
    license_duration = 15
    days_to_license_end =  license_duration - (datetime_now - datetime_joined).days

    # url for request        
    url = '/trial-license-check'
    # data for request
    data = {'license_duration': license_duration}
    # get request to url with data in json format 
    response = self.client.generic(method='GET', path=url, data=json.dumps(data), content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['days_to_license_end'], days_to_license_end)

  def test_check_trial_license_for_user_with_ended_license(self):
    """
    Test attempt to check trial license for user with ended license.
    """
    # test user
    test_username = 'user_with_ended_license'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)

    # calculate days to license end
    datetime_now = timezone.now()
    datetime_joined = test_user.date_joined 
    license_duration = 30
    days_to_license_end =  license_duration - (datetime_now - datetime_joined).days
    # test assertion
    self.assertTrue(days_to_license_end < 0)

    # url for request        
    url = '/trial-license-check'
    # get request to url 
    response = self.client.generic(method='GET', path=url, content_type='application/json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['days_to_license_end'], 0)

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


class UserFilesListViewTests(APITestCase):

  def test_get_user_files_list_with_valid_token(self):
    """
    Test attempt to get user files list with valid token.
    """
    # test username
    test_username = 'paulina'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)
    # url for request        
    url = '/user-files'
    # get request to url
    response = self.client.get(url, format='json')
    # test assertion
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_get_user_files_list_with_invalid_token(self):
    """
    Test attempt to get user files list with invalid token.
    """
    # mannually add invalid credentials to all requests from client 
    self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_token'))
    # url for request        
    url = '/user-files'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

  def test_get_user_files_list_without_token_header(self):
    """
    Test attempt to get user files list without token header.
    """
    # url for request        
    url = '/user-files'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

  def test_get_user_files_list_returns_valid_data(self):
    """
    Test attempt to get user files list that return valid data.
    """
    # test username
    test_username = 'paulina'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)
    # url for request  
    url = '/user-files'
    # get request to url 
    response = self.client.get(url, format='json')

    # test assertions
    # assert that result contains all required fields (they are presented in serializers classes)
    first_user_file_data = response.data['results'][0]
    self.assertTrue('id' in first_user_file_data)
    self.assertTrue('file' in first_user_file_data)
    self.assertTrue('post_date' in first_user_file_data)
    
    # assert that using request we can get all user files
    self.assertEqual(response.data['count'], File.objects.all().filter(user=test_user).count())

    # assert that results contains only 10 elements (page size)
    self.assertEqual(len(response.data['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])

    # UserFilesListView sorts results by id in descending order so we can assert that all ids are sorted
    all_page_ids = [user_file['id'] for user_file in response.data['results']]
    ids_iterator = iter(all_page_ids)
    _ = ids_iterator.__next__()
    self.assertTrue(all(prev_idx > next_idx for prev_idx, next_idx in zip(all_page_ids, ids_iterator)))

    # assert that all returned files are owned by our test user
    test_user_files_ids_list = list(File.objects.all().filter(user=test_user).values('id'))
    test_user_files_ids = [query_set_dict['id'] for query_set_dict in test_user_files_ids_list]
    self.assertTrue(all(id in test_user_files_ids for id in all_page_ids))

  def test_get_user_files_list_returns_valid_redirection_chains(self):
    """
    Test attempt to get user files list that return correct redirection chains.
    """
    # test username
    test_username = 'paulina'
    # we can force authenticate user to bypass explicit token usage
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)

    # calculate number of pages
    num_pages = math.ceil(File.objects.all().filter(user=test_user).count() / settings.REST_FRAMEWORK['PAGE_SIZE'])

    # url for request  
    url = '/user-files'
    # get request to url with following all redirections 
    response = self.client.get(url, format='json')

    # test assertions
    # assert that response data hasn't refer to previous page (as it's first page) 
    self.assertTrue(response.data['previous'] is None)
    # assert that response data has refer to next page (is not None) if number of pages is more than 1 
    has_next = num_pages > 1 
    self.assertEqual(response.data['next'] is not None, has_next)

    # check redirection to next page
    visited_pages = 1
    while visited_pages <= NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
        next_url = response.data['next']
        if next_url is not None:
            response = self.client.get(next_url, format='json')
            visited_pages += 1
            self.assertTrue(response.data['previous'] is not None)
        else:
            break

    url += '?page={}'.format(num_pages)
    response = self.client.get(url, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # assert that response data hasn't refer to next page (is None) 
    self.assertTrue(response.data['next'] is None)


class AllFilesListViewTests(APITestCase):

  def test_get_all_files_list_with_valid_token(self):
    """
    Test attempt to get all files list with valid token.
    """
    # test username
    test_username = 'paulina'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)
    # url for request        
    url = '/all-files'
    # get request to url
    response = self.client.get(url, format='json')
    # test assertion
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_get_all_files_list_with_invalid_token(self):
    """
    Test attempt to get all files list with invalid token.
    """
    # mannually add invalid credentials to all requests from client 
    self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_token'))
    # url for request        
    url = '/all-files'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

  def test_get_all_files_list_without_token_header(self):
    """
    Test attempt to get all files list without token header.
    """
    # url for request        
    url = '/all-files'
    # get request to url 
    response = self.client.get(url, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

  def test_get_all_files_list_returns_valid_data(self):
    """
    Test attempt to get all files list that return valid data.
    """
    # test username
    test_username = 'paulina'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)
    # url for request  
    url = '/all-files'
    # get request to url 
    response = self.client.get(url, format='json')

    # test assertions
    # assert that result contains all required fields (they are presented in serializers classes)
    first_file_data = response.data['results'][0]
    self.assertTrue('id' in first_file_data)
    self.assertTrue('username' in first_file_data)
    self.assertTrue('file' in first_file_data)
    self.assertTrue('post_date' in first_file_data)
    
    # assert that using request we can get all files
    self.assertEqual(response.data['count'], File.objects.all().count())

    # assert that results contains only 10 elements (page size)
    self.assertEqual(len(response.data['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])

    # AllFilesListView sorts results by id in descending order so we can assert that all ids are sorted
    all_page_ids = [user_file['id'] for user_file in response.data['results']]
    ids_iterator = iter(all_page_ids)
    _ = ids_iterator.__next__()
    self.assertTrue(all(prev_idx > next_idx for prev_idx, next_idx in zip(all_page_ids, ids_iterator)))

  def test_get_all_files_list_returns_valid_redirection_chains(self):
    """
    Test attempt to get all files list that return correct redirection chains.
    """
    # test username
    test_username = 'paulina'
    # we can force authenticate user to bypass explicit token usage
    test_user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=test_user)

    # calculate number of pages
    num_pages = math.ceil(File.objects.all().count() / settings.REST_FRAMEWORK['PAGE_SIZE'])

    # url for request  
    url = '/all-files'
    # get request to url with following all redirections 
    response = self.client.get(url, format='json')

    # test assertions
    # assert that response data hasn't refer to previous page (as it's first page) 
    self.assertTrue(response.data['previous'] is None)
    # assert that response data has refer to next page (is not None) if number of pages is more than 1 
    has_next = num_pages > 1 
    self.assertEqual(response.data['next'] is not None, has_next)

    # check redirection to next page
    visited_pages = 1
    while visited_pages <= NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
        next_url = response.data['next']
        if next_url is not None:
            response = self.client.get(next_url, format='json')
            visited_pages += 1
            self.assertTrue(response.data['previous'] is not None)
        else:
            break

    url += '?page={}'.format(num_pages)
    response = self.client.get(url, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # assert that response data hasn't refer to next page (is None) 
    self.assertTrue(response.data['next'] is None)


class PostFileViewTests(APITestCase):
    
  def test_create_file_with_valid_token(self):
    """
    Test attempt to create file with valid token.
    """
    file_counts = File.objects.all().count()
    # test username
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=user)
    # url for request 
    url = '/post-file'
    # data for request
    test_filename = 'file_to_test_post_request.jpg'
    test_file_path = os.path.join(settings.BASE_DIR, 'uniphoto', 'test', 'test_data', test_filename)
    test_file = SimpleUploadedFile(test_filename, open(test_file_path, 'rb').read(), content_type='multipart/form-data')
    data = {'file': test_file}
    # post request to url with data in multipart format 
    response = self.client.post(url, data, format='multipart')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(File.objects.all().count(), file_counts + 1)
    self.assertEqual(File.objects.all().latest('id').user.id, user.id)
    self.assertEqual(File.objects.all().latest('id').file.name, test_filename)
    self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, test_filename)))

  def test_create_file_with_invalid_token(self):
    """
    Test attempt to create file with invalid token.
    """
    # mannually add invalid credentials to all requests from client 
    self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_token'))
    # url for request        
    url = '/post-file'
    # post request to url
    response = self.client.post(url, format='multipart')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

  def test_create_file_without_token_header(self):
    """
    Test attempt to create file without token header.
    """
    # url for request        
    url = '/post-file'
    # post request to url
    response = self.client.post(url, format='multipart')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

  def test_create_file_with_unsupported_extension(self):
    """
    Test attempt to create file with unsupported extension.
    """
    file_counts = File.objects.all().count()
    # test username
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=user)
    # url for request 
    url = '/post-file'
    # data for request
    test_filename = 'file_to_test_post_request_with_unsupported_extension.png'
    test_file_path = os.path.join(settings.BASE_DIR, 'uniphoto', 'test', 'test_data', test_filename)
    test_file = SimpleUploadedFile(test_filename, open(test_file_path, 'rb').read(), content_type='multipart/form-data')
    data = {'file': test_file}
    # post request to url with data in multipart format 
    response = self.client.post(url, data, format='multipart')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'file': [ErrorDetail('Unsupported file extension. Supported file extensions: .jpg, .jpeg, .mp4', code='invalid')], 
                                    })
    self.assertEqual(File.objects.all().count(), file_counts)
    self.assertNotEqual(File.objects.all().latest('id').file.name, test_filename)
    self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, test_filename)))

  def test_create_file_with_invalid_data(self):
    """
    Test attempt to create file with invalid data.
    """
    file_counts = File.objects.all().count()
    # test username
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=user)
    # url for request 
    url = '/post-file'
    # data for request
    data = {'file': 353.905}
    # post request to url with data in multipart format 
    response = self.client.post(url, data, format='multipart')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'file': [ErrorDetail('The submitted data was not a file. Check the encoding type on the form.', code='invalid')], 
                                    })
    self.assertEqual(File.objects.all().count(), file_counts)

  def test_create_file_with_blank_fields(self):
    """
    Test attempt to create file with blank fields.
    """
    file_counts = File.objects.all().count()
    # test username
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=user)
    # url for request 
    url = '/post-file'
    # data for request
    data = {'file': None}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'file': [ErrorDetail('This field may not be null.', code='null')], 
                                    })
    self.assertEqual(File.objects.all().count(), file_counts)

  def test_create_file_without_fields(self):
    """
    Test attempt to create file without required fields.
    """
    file_counts = File.objects.all().count()
    # test username
    test_username = 'azalia'
    # we can force authenticate user to bypass explicit token usage when we don't need to test it
    user = User.objects.get(username=test_username)
    self.client.force_authenticate(user=user)
    # url for request 
    url = '/post-file'
    # data for request
    data = {'fake_file': 'fake_file'}
    # post request to url with data in multipart format 
    response = self.client.post(url, data, format='multipart')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'file': [ErrorDetail('No file was submitted.', code='required')], 
                                    })
    self.assertEqual(File.objects.all().count(), file_counts)