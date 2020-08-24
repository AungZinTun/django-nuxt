The tutorial has been split into two parts- setting up the backend, and setting up the frontend.

The repo has two branches: `part-1` and `part-2`. `part-1` contains the files for this tutorial, `part-2` contains
the files for this tutorial and the next.

Tutorial Part 2: [Here](https://dev.to/ignisda/setting-up-user-authentication-with-nuxtjs-and-django-rest-framework-part-2-4a6e-temp-slug-7247513?preview=f312affddd901ef65a7b7e79c86ed69d93b47a4c3786097a3ce8bd30c6bcce0c049e720674f1e9d8821f3fd0575555d87adb44588940767d0b11e58f)

**GITHUB REPO:** https://github.com/IgnisDa/django-nuxtjs-authentication

We'll be using Token Authentication using the [djoser](https://www.google.com/url?q=https://djoser.readthedocs.io/en/latest/) package to
implement an authentication backend API, and consume it with a Nuxtjs frontend.

_NOTE:_ For the sake of brevity, I will omit all comments
explaining the working. However, the code is well commented
and can be accessed via the github repository.

# Prerequisites

1. Familiarity with django-rest-framework
2. Knowledge of nuxt-auth: [this video will be enough](https://m.youtube.com/watch?v=zzUpO8tXoaw)

# Setting up the backend

Install the following packages in your virtual environment:

- django
- djangorestframework
- djoser
- django-cors-headers
- httpie
- validate-email

Start by making a common directory `nuxtjs+drf-user-auth/` where the frontend (nuxtjs) and backend (django rest framework) will live separately in
`frontend/` and `backend/` directories respectively.

```bash
mkdir nuxtjs+drf-user-auth && cd nuxtjs+drf-user-auth/
django-admin startproject backend && cd backend/
python manage.py startapp accounts
```

Add the new app and addons to `settings.py`.

```python
# backend/settings.py
INSTALLED_APPS = [
  # other stuff
  'rest_framework',
  'rest_framework.authtoken',
  'corsheaders',
  'accounts.apps.AccountsConfig',
]
```

Next, we define a custom user model that will handle user authentication for us. This will allow us to add more fields to the user model than
what the default `django.contrib.auth.models.User` provides, and also
use `email` as the default identifier instead of `username`.

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import managers # we will write this file shortly


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField()
    gender = models.CharField(
        max_length=140,
        null=True,
        choices=(
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        )
    )
    birth_date = models.DateField(null=True, blank=True)
    pro = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = managers.CustomUserManager()

    def __str__(self):
        return f"{self.email}'s custom account"

# accounts/managers.py
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from validate_email import validate_email


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        if not validate_email(email):
            raise ValueError(_('Invalid email set'))
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

```

Add the relevant settings in your `settings.py` file.

```python
# backend/settings.py
AUTH_USER_MODEL = 'accounts.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

Then, we set up basic urls.

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('', include('djoser.urls.authtoken')),
    path('admin/', admin.site.urls),
]
```

Run `makemigrations`, `migrate`, and create a new superuser using
`createsuperuser`. Fire up a development server using `runserver`, and
then visit `token/login/` in your browser. Enter the correct credentials
and check that you get a token as a response in the `auth_token`
property. Also visit `token/logout/`, though it will be unusable.

Next we set up serializers for our `CustomUser` model.

```python
# accounts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers, validators

CustomUser = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        write_only=True, validators=[validators.UniqueValidator(
            message='This email already exists',
            queryset=CustomUser.objects.all()
        )]
    )
    password = serializers.CharField(write_only=True)
    birth_date = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    birth_date = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',
                  'password', 'bio', 'gender', 'birth_date')


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    birth_date = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',
                  'bio', 'gender', 'birth_date', 'id')
```

Then we define the views and viewsets that will use these serializers to deliver the data to the frontend.

```python
# accounts/views.py
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from . import serializers

CustomUser = get_user_model()


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserRetrieveSerializer
    permission_classes = (permissions.IsAuthenticated,)


    def get_object(self):
        return self.request.user

# accounts/viewsets.py
from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from . import serializers

CustomUser = get_user_model()


class CustomUserModelViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CustomUserSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = CustomUser.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

# accounts/routers.py
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register('', viewsets.CustomUserModelViewSet)


# accounts/urls.py
from django.urls import include, path

from . import routers, views

urlpatterns = [
    path('data/', views.UserRetrieveUpdateDestroyAPIView.as_view(),
         name='user-data'),
    path('users/', include(routers.router.urls)),
]
```

The new urls will expose a few endpoints for the following purposes:

| METHOD     | PATH                   | PURPOSE                                                                                                          |
| ---------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| GET        | accounts/data/         | Retrieve data of the currently logged in user. Anonymous users can not access this page.                         |
| GET        | accounts/users/        | A list of all the users in the database.                                                                         |
| POST       | accounts/users/        | Create a new user using the data that accompanies the POST request.                                              |
| PATCH/ PUT | accounts/users/`<pk>`/ | Update, or change all user details for user with this `pk`.                                                      |
| POST       | token/login/           | Send a `POST` request with the correct credentials and this will respond with a login token called `auth_token`. |
| POST       | token/logout/          | Send a `POST` request with the `auth_token` in the header and the corresponding user will be logged out.         |

Let us use `httpie` to check whether
our endpoints work.

```bash
# Register a new user
$ http POST http://127.0.0.1:8000/accounts/users/ email='email1@email.com' password="test-pass" first_name="Dabreil" last_name="Ignis"
{
    "bio": "",
    "birth_date": null,
    "first_name": "Dabreil",
    "gender": null,
    "last_name": "Ignis"
}

# Login using the new user
# You can visit `admin/authtoken/token/` to see the new token generated
$ http POST http://127.0.0.1:8000/token/login/ email='email1@email.com' password="test-pass"
{
    "auth_token": "b1a73afd0431c87b5e0c4afb4b085d401d652edb"
}

# Access data using  the token generated. Make sure you use the correct token that you got in the above step
$ http GET http://127.0.0.1:8000/accounts/data/ "Authorization: Token b1a73afd0431c87b5e0c4afb4b085d401d652edb"
{
    "bio": "",
    "birth_date": null,
    "email": "email1@email.com",
    "first_name": "Dabreil",
    "gender": null,
    "id": 3,
    "last_name": "Ignis"
}

# Logout the user
$ http POST http://127.0.0.1:8000/token/logout/ 'Authorization: Token b1a73afd0431c87b5e0c4afb4b085d401d652edb'
# You won't get a response but the token will be deleted from the database. Check this from the admin.
```

Yay! It all works! Now we only need to add a few settings
to make sure that our frontend can communicate with
our backend using the `django-corsheaders` package.

```python
# backend/settings.py
CORS_ORIGIN_WHITELIST = ('http://127.0.0.1:3000',)
```

This is the default development server that Nuxtjs uses. You can configure yours accordingly. That's it for this part.

Make sure you checkout the Part-2 to learn how to add authentication to your Nuxtjs frontend.

Tutorial Part 2: [Here](https://dev.to/ignisda/setting-up-user-authentication-with-nuxtjs-and-django-rest-framework-part-2-4a6e-temp-slug-7247513?preview=f312affddd901ef65a7b7e79c86ed69d93b47a4c3786097a3ce8bd30c6bcce0c049e720674f1e9d8821f3fd0575555d87adb44588940767d0b11e58f)
