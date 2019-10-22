import os
import channels_redis

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '77!1##-%^a2yfmd^s%3uyva=85!myi9ri6is$sh-i1pd0o(5)k'
#SECRET_KEY = '@=@3q!0@w28e+s783bfsklyt*2r)-9((e23fizstjm$1b9rn29'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#DEBUG = True

ALLOWED_HOSTS = ['www.objectivemoney.org','objectivemoney.org','45.55.48.199','localhost','127.0.0.1']

DATA_UPLOAD_MAX_MEMORY_SIZE = 3*1024*1024

FILE_UPLOAD_PERMISSIONS=0o640

# Application definition

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
]

ASGI_APPLICATION = "obmo.routing.application"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
            #"hosts": [("redis://:mypassword@127.0.0.1:6379/0")],
        },
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'obmo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'obmo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'obmo', 
        'USER': 'dbadmin', 
        'PASSWORD': 'Toilavua694', 
        'HOST': 'localhost', 
        'PORT': '5432', 
  }
}





# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql', 
#         'NAME': 'obmo7', 
#         'USER': 'postgres', 
#         'PASSWORD': 'toithichmia', 
#         'HOST': 'localhost', 
#         'PORT': '5432', 
#   }
# }





# ce5629c6dd560556c42fcf50b0d45a8e7838279926d5962f222353531ba036e6
# 7d4a680dd59fad92302aba616f449f98d3064862ef0e2187892c8a97574c8a0e


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/myaccount'
LOGIN_URL = '/login' 


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

#STATIC_ROOT = os.path.join(BASE_DIR,"static_files")

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, "static"),
# )


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# 74cb714e483c34d8a346eb80bab6954ccee63c6fbfc20f972ee71db80a9e68b1
# 2afbe47ab562b48ead387e835c961cc06514d2496cad57505b521051f6593783
# 3b1c4f583b3296abb6e855943843039c4d18067c97a1e505d3c8f4284e4f912d