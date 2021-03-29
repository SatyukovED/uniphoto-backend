from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from django.contrib.auth.models import User
from uniphoto.models import File


class SignUpTests(APITestCase):

  def test_create_valid_account(self):
    """
    Test attempt to sign up User with valid data.
    """
    user_counts = User.objects.count()
    # url for request 
    url = '/registration'
    # data for request
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data, {'email': 'nastya@uniphoto.com', 'username': 'nastya'})
    self.assertEqual(User.objects.count(), user_counts + 1)
    self.assertEqual(User.objects.latest('id').email, 'nastya@uniphoto.com')
    self.assertEqual(User.objects.latest('id').username, 'nastya')

  def test_create_account_with_invalid_email(self):
    """
    Test attempt to sign up User with invalid email. 
    """
    user_counts = User.objects.count()
    # url for request 
    url = '/registration'
    # data for request
    data = {'email': 'nastyauniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {'email': [ErrorDetail('4', code='invalid')]})
    self.assertEqual(User.objects.count(), user_counts)
    self.assertNotEqual(User.objects.latest('id').email, 'nastya@uniphoto.com')
    self.assertNotEqual(User.objects.latest('id').username, 'nastya')

  def test_create_account_with_blank_fields(self):
    """
    Test attempt to sign up User with blank fields.
    """
    user_counts = User.objects.count()
    # url for request 
    url = '/registration'
    # data for request
    data = {'email': '', 'username': '', 'password': ''}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'email': [ErrorDetail('3', code='blank')], 
                                        'username': [ErrorDetail('3', code='blank')], 
                                        'password': [ErrorDetail('3', code='blank')]
                                    })
    self.assertEqual(User.objects.count(), user_counts)
    self.assertNotEqual(User.objects.latest('id').email, 'nastya@uniphoto.com')
    self.assertNotEqual(User.objects.latest('id').username, 'nastya')

  def test_create_account_without_fields(self):
    """
    Test attempt to sign up User without required fields.
    """
    user_counts = User.objects.count()
    # url for request 
    url = '/registration'
    # data for request
    data = {'fake_email': 'fake_nastya@uniphoto.com', 'fake_username': 'fake_nastya'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'email': [ErrorDetail('2', code='required')], 
                                        'username': [ErrorDetail('2', code='required')], 
                                        'password': [ErrorDetail('2', code='required')]
                                    })
    self.assertEqual(User.objects.count(), user_counts)
    self.assertNotEqual(User.objects.latest('id').email, 'nastya@uniphoto.com')
    self.assertNotEqual(User.objects.latest('id').username, 'nastya')

  def test_create_account_with_same_email_and_username(self):
    """
    Test attempt to sign up User with already exist email and username.
    """
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')

    user_counts = User.objects.count()
    user_id = User.objects.latest('id').id
    # url for request 
    url = '/registration'
    # data for request
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop_new'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'email': [ErrorDetail('1', code='unique')], 
                                        'username': [ErrorDetail('1', code='unique')]
                                    })
    self.assertEqual(User.objects.count(), user_counts)
    self.assertEqual(User.objects.latest('id').id, user_id)

  def test_create_account_with_short_password(self):
    """
    Test attempt to sign up User with password length less min_length.
    """
    user_counts = User.objects.count()
    # url for request 
    url = '/registration'
    # data for request
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastya'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {'password': [ErrorDetail('5', code='min_length')]})
    self.assertEqual(User.objects.count(), user_counts)
    self.assertNotEqual(User.objects.latest('id').email, 'nastya@uniphoto.com')
    self.assertNotEqual(User.objects.latest('id').username, 'nastya')


class SignInTests(APITestCase):

  def test_sign_in_with_valid_data(self):
    """
    Test attempt to sing in User with valid data.
    """
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')

    # url for request 
    url = '/api-token-auth'
    # data for request
    data = {'username': 'nastya', 'password': 'nastyakpop'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # user token given after sign in 
    user_token = str(User.objects.latest('id').auth_token)
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, {'token': user_token})

  def test_sign_in_with_invalid_username(self):
    """
    Test attempt to sing in User with invalid username.
    """
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')

    # url for request 
    url = '/api-token-auth'
    # data for request
    data = {'username': 'nastyaa', 'password': 'nastyakpop'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {'non_field_errors': [ErrorDetail('Unable to log in with provided credentials.', code='authorization')]})

  def test_sign_in_with_invalid_password(self):
    """
    Test attempt to sing in User with invalid password.
    """
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')

    # url for request 
    url = '/api-token-auth'
    # data for request
    data = {'username': 'nastyaa', 'password': 'nastyaloveskpop'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {'non_field_errors': [ErrorDetail('Unable to log in with provided credentials.', code='authorization')]})

  def test_sign_in_with_blank_fields(self):
    """
    Test attempt to sing in User with blank fields.
    """
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')

    # url for request 
    url = '/api-token-auth'
    # data for request
    data = {'username': '', 'password': ''}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'username': [ErrorDetail('This field may not be blank.', code='blank')], 
                                        'password': [ErrorDetail('This field may not be blank.', code='blank')]
                                    })

  def test_sign_in_without_fields(self):
    """
    Test attempt to sing in User without fields.
    """
    url = '/registration'
    data = {'email': 'nastya@uniphoto.com', 'username': 'nastya', 'password': 'nastyakpop'}
    response = self.client.post(url, data, format='json')

    # url for request 
    url = '/api-token-auth'
    # data for request
    data = {'fake_username': 'fake_nastya'}
    # post request to url with data in json format 
    response = self.client.post(url, data, format='json')
    # test assertions
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {
                                        'username': [ErrorDetail('This field is required.', code='required')], 
                                        'password': [ErrorDetail('This field is required.', code='required')]
                                    })