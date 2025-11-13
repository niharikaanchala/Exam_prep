"""
Django settings for backend project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-&haow7^fneqb041ku_xojcsiog#@(ev21g-3)p0py%fmpps0@&'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    # 'exams.apps.ExamsConfig', 
    'practice_tests',
    'categories',
    'exams',
    'common',
    'enrollments',
    'settings_app',
    'home',
    'blog',
    'dashboard',
    'corsheaders',
    'rest_framework',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


ROOT_URLCONF = 'backend.urls'
# AUTH_USER_MODEL = 'user_profile.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# # Database (Djongo / MongoDB)
# DATABASES = {
#     'default': {
#         'ENGINE': 'djongo',
#         'NAME': 'mock-test',  # your MongoDB database name
#         'CLIENT': {
#             'host': 'mongodb+srv://anchalaniharika_db_user:Niharika2002@cluster0.0quwioe.mongodb.net/mock-test?retryWrites=true&w=majority'
#         }
#     }
# }


from mongoengine import connect

connect(
    db="mock-test",
    host="mongodb+srv://anchalaniharika_db_user:Niharika2002@cluster0.0quwioe.mongodb.net/mock-test?retryWrites=true&w=majority"
)


# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Razorpay Configuration
RAZORPAY_KEY_ID = 'rzp_test_gzd0pzBqOopBBl'  # Add your Razorpay Key ID here
RAZORPAY_KEY_SECRET = 'DQewqJImITIliHknSsLdeDG4'  # Add your Razorpay Key Secret here
