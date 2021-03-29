Run server\
python manage.py runserver

Run tests\
python manage.py test

Run tests with coverage evaluating\
coverage erase\
coverage run manage.py test\
coverage report\
coverage html

Start up DB / If changes were made in DB\
python manage.py makemigrations\
python manage.py makemigrations uniphoto\
python manage.py migrate
