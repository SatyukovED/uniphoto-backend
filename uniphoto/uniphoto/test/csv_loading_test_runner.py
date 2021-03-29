from django.test.runner import DiscoverRunner
from django.conf import settings
from django.db import connection
import os
import shutil


settings.MEDIA_ROOT += '\\test'


class CSVLoadingTestRunner(DiscoverRunner):

  def setup_databases(self, *args, **kwargs):
    old_names = super(CSVLoadingTestRunner, self).setup_databases(*args, **kwargs)
    with connection.cursor() as cursor:
      test_data_path = os.path.join(settings.BASE_DIR, 'uniphoto', 'test', 'test_data')
      user_csv_path = os.path.join(test_data_path, 'user.csv')
      file_csv_path = os.path.join(test_data_path, 'file.csv')
      test_media_path = os.path.join(test_data_path, 'test_media')
      shutil.copytree(test_media_path, settings.MEDIA_ROOT)
      cursor.execute("""
                     COPY auth_user(username, email, password, is_superuser, is_staff, is_active, first_name, last_name, date_joined)
                     FROM %s
                     DELIMITER ','
                     CSV HEADER;
                     """, [user_csv_path])
      cursor.execute("""
                     COPY uniphoto_file(file, user_id, post_date)
                     FROM %s
                     DELIMITER ','
                     CSV HEADER;
                     """, [file_csv_path])
    return old_names

  def teardown_databases(self, *args, **kwargs):
    shutil.rmtree(settings.MEDIA_ROOT)
    with connection.cursor() as cursor:
      cursor.execute("""
                     DELETE FROM uniphoto_file;
                     """)
      cursor.execute("""
                     DELETE FROM auth_user;
                     """)
    super(CSVLoadingTestRunner, self).teardown_databases(*args, **kwargs)
