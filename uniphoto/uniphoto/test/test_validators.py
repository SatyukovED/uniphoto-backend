from django.test import TestCase
from django.core.exceptions import ValidationError
from uniphoto.validators import validate_file_extension
from dataclasses import dataclass


@dataclass
class TestFile:
  path: str
  name: str

class ValidateFileExtensionTests(TestCase):

  def test_validate_file_extension(self):
    test_file = TestFile('', 'testfile.mp3')
    try:
      validate_file_extension(test_file)
    except ValidationError as error:
      self.assertEqual(error.message_dict['message'], ['Unsupported file extension. Supported file extensions: .jpg, .jpeg, .mp4'])