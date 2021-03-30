from django.test import TestCase
from django.core.exceptions import ValidationError
from uniphoto.validators import validate_file_extension
from dataclasses import dataclass


@dataclass
class TestFile:
  path: str
  name: str

class ValidateFileExtensionTests(TestCase):

  def test_validate_file_extension_for_file_with_supported_extension(self):
    """
    Test attempt to validate file with supported extension.
    """
    test_file = TestFile('', 'testfile.mp4')
    error_raised = False
    try:
      validate_file_extension(test_file)
    except:
      error_raised = True
    self.assertFalse(error_raised)
      
  def test_validate_file_extension_for_file_with_unsupported_extension(self):
    """
    Test attempt to validate file with unsupported extension.
    """
    test_file = TestFile('', 'testfile.mp3')
    try:
      validate_file_extension(test_file)
    except ValidationError as error:
      self.assertEqual(error.message_dict['message'], ['Unsupported file extension. Supported file extensions: .jpg, .jpeg, .mp4'])