ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

SECRET_KEY = '{{ secret_key }}'
SERVER_URL = '{{ server_url }}'

DATABASES = {'default': {'USER': None}}# initialize dict
DATABASES['default']['USER'] = '{{ default_db_user }}'
