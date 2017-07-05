"""
Django settings for mysite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
common_path = os.path.join(BASE_DIR, 'Common/Common/Python')
sys.path.append(common_path)
import pdb; pdb.set_trace()
from Common.Files import file_access

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'mysite/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fc^(a7u90fl6lyh$$o(vn=e_33p+t=ai@t_!8pnneizjhg2vwq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scisheets',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
_BASE_DB_NAME = 'db.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, _BASE_DB_NAME),
        'TEST_NAME': os.path.join(BASE_DIR, 'TEST' + _BASE_DB_NAME),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "mysite/static"),
    )

# Heatmap constants
UPLOAD_FILE_TABLE = 'heatmap_uploadedfiles'
UPLOAD_DIR = os.path.join(BASE_DIR, 'mysite/uploads/')

# Scisheets constants
SCISHEETS_USER_PYDIR = os.path.join(BASE_DIR, 'user/guest/python')
SCISHEETS_USER_TBLDIR = os.path.join(BASE_DIR, 'user/guest/tables')
SCISHEETS_USER_TBLDIR_BACKUP = os.path.join(BASE_DIR, 
    'user/guest/tables/backup')
SCISHEETS_PLUGIN_PYDIR = os.path.join(BASE_DIR, 'scisheets/plugins')
SCISHEETS_PLUGIN_PYPATH = 'scisheets.plugins'
SCISHEETS_MAX_TABLE_VERSIONS = 10
SCISHEETS_EXT = "scish"
SCISHEETS_DEFAULT_TABLEFILE = os.path.join(SCISHEETS_USER_TBLDIR, 
    "scisheet_table.%s" % SCISHEETS_EXT)
SCISHEETS_TEST_DIR = os.path.join(BASE_DIR, 'scisheets/core/test_dir')
SCISHEETS_FORMULA_EVALUATION_MAX_ITERATIONS = 40
SCISHEETS_LOG = os.path.join(BASE_DIR, 'scisheets_log.csv')
