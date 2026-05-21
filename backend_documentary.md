# Event Registration System — Complete Step-by-Step Developer Documentary

This guide documents the complete engineering process for building a robust, role-based, secure event registration backend using Django, Django REST Framework (DRF), and PostgreSQL. 

---

## Table of Contents
1. **System Architecture & Key Concepts**
2. **Phase 1: Environment Setup & Project Scaffolding**
3. **Phase 2: The Users & Authentication App**
4. **Phase 3: The Event Management App**
5. **Phase 4: The Registrations App**
6. **Phase 5: Database Setup, Migrations & Launch**
7. **Phase 6: Testing Manual (Admin, Browser, and Postman)**

---

## 1. System Architecture & Key Concepts

We design this system using a modern, multi-tiered REST API architecture:

*   **Authentication (JWT)**: Stateless authentication via Json Web Tokens using `djangorestframework-simplejwt`. The client logs in, receives a pair of tokens (Access & Refresh), and sends the Access token in the HTTP `Authorization: Bearer <token>` header for protected endpoints.
*   **Role-Based Access Control (RBAC)**: Users belong to one of three roles:
    1.  `USER`: Can list/view events, register for an event, view their own registrations, and cancel their registrations.
    2.  `ORGANIZER`: Can do everything a User can, plus create events, list events they created, and view registrations for their events.
    3.  `ADMIN`: Full control over all records.
*   **Safe Database Concurrency**: In high-demand event scenarios (like tickets selling out), multiple requests might attempt to register at the exact same split-second. To prevent overbooking beyond capacity, we use PostgreSQL's `SELECT ... FOR UPDATE` via Django's `.select_for_update()`. This locks the capacity count operation until the database transaction is saved.

---

## 2. Phase 1: Environment Setup & Project Scaffolding

### Step 1: Install Dependencies
Open your command terminal (Command Prompt or PowerShell) and run:
```bash
pip install django djangorestframework psycopg2-binary djangorestframework-simplejwt django-environ django-cors-headers
```
*   `django`: The core web framework.
*   `djangorestframework`: Adds REST serialization, views, and authentications.
*   `psycopg2-binary`: Database adapter enabling Django to talk to PostgreSQL.
*   `djangorestframework-simplejwt`: Implementation of JSON Web Tokens.
*   `django-environ`: Safely loads database passwords and secrets from a `.env` file instead of committing credentials to GitHub.
*   `django-cors-headers`: Allows frontend frameworks (like React, Angular, or Vue) running on different ports to connect to this API.

### Step 2: Initialize Project and Apps
Run the following commands to create the main project configuration folder and three specialized app directories:
```bash
# Create the project structure
django-admin startproject config .

# Create the applications
python manage.py startapp users
python manage.py startapp events
python manage.py startapp registrations
```

### Step 3: Write Settings (`config/settings.py`)
This file is the configuration center. It handles database credentials, registers dependencies, and configures authentication policies.
Create or replace the contents of **`config/settings.py`**:
```python
import environ
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file variables
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party packages
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # Local Apps
    "users",
    "events",
    "registrations",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Handles cross-origin requests
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database Configuration using environment variables
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# Link Custom User model
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings (forcing JWT authentication)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# JWT configurations
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOW_ALL_ORIGINS = True
```

---

## 3. Phase 2: The Users & Authentication App

The default Django User model uses `username` to log in and lacks a customized role field. To address this, we build a custom User app.

### 1. Define Constants (`users/constants.py`)
To avoid hardcoding roles (e.g. `'USER'`, `'ORGANIZER'`, `'ADMIN'`) in several views or templates, we declare them once in a dedicated constants file.
```python
ROLE_USER = "USER"
ROLE_ORGANIZER = "ORGANIZER"
ROLE_ADMIN = "ADMIN"

ROLE_CHOICES = [
    (ROLE_USER, "User"),
    (ROLE_ORGANIZER, "Organizer"),
    (ROLE_ADMIN, "Admin"),
]
```

### 2. Define Custom User Manager (`users/managers.py`)
Since we log in with **email** instead of username, we must rewrite Django's User creation manager:
```python
from django.contrib.auth.models import BaseUserManager
from .constants import ROLE_USER, ROLE_ADMIN

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, role=ROLE_USER, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        if not username:
            raise ValueError("Username is required.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, role=ROLE_ADMIN, **extra_fields)
```

### 3. Define Custom User Model (`users/models.py`)
This holds user credentials, and defines roles:
```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from .constants import ROLE_USER, ROLE_CHOICES

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"  # Identifies user during auth
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.username} ({self.role})"
```

### 4. Define Serializers (`users/serializers.py`)
Serializers act as data parsers: converting Django model instances into JSON (read-only queries) and validating user inputs (creating accounts/logging in).
```python
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from .constants import ROLE_CHOICES

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "role"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get("email"), password=attrs.get("password"))
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
```

### 5. Define Authentication Views (`users/views.py`)
These views receive the web request, trigger validation, generate tokens, and output responses.
```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
                "tokens": generate_tokens(user)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return Response({
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "tokens": generate_tokens(user)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
```

### 6. Map Auth URLs (`users/urls.py`)
```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
```

### 7. Register Custom Admin Dashboard (`users/admin.py`)
Configures the Django Admin console to show user roles and details:
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "role", "is_staff")
    list_filter = ("role", "is_staff")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Permissions", {"fields": ("role", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "role", "password"),
        }),
    )
    filter_horizontal = ()
```

---

## 4. The Event Management App

We create the Events app to allow organizers to build events, and everyone to read them.

### 1. Write Permissions (`events/permissions.py`)
Custom DRF classes validating requesting users:
```python
from rest_framework.permissions import BasePermission

class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "ORGANIZER"

class IsEventOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        return obj.organizer == request.user
```

### 2. Define Model (`events/models.py`)
```python
from django.db import models
from django.conf import settings

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "events"
        ordering = ["date"]

    def __str__(self):
        return self.name

    @property
    def available_slots(self):
        active_registrations = self.registrations.filter(status="ACTIVE").count()
        return self.capacity - active_registrations
```

### 3. Write Serializers (`events/serializers.py`)
Handles validation rules:
1. Dates must be future dates.
2. Capacity must be greater than 0.
```python
from django.utils import timezone
from rest_framework import serializers
from .models import Event
from users.serializers import UserSerializer

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "description", "date", "location", "capacity", "organizer", "available_slots"]

    def validate_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Event date must be in the future.")
        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than zero.")
        return value
```

### 4. Create Event Views (`events/views.py`)
```python
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Event
from .serializers import EventSerializer
from .permissions import IsOrganizer, IsEventOwnerOrAdmin

class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class EventUpdateView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsEventOwnerOrAdmin]

class EventDeleteView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsEventOwnerOrAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Event deleted successfully."}, status=status.HTTP_200_OK)

class MyEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
```

### 5. Map Event URLs (`events/urls.py`)
```python
from django.urls import path
from .views import EventListView, EventDetailView, EventCreateView, EventUpdateView, EventDeleteView, MyEventsView

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("my/", MyEventsView.as_view(), name="my-events"),
    path("create/", EventCreateView.as_view(), name="event-create"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("<int:pk>/update/", EventUpdateView.as_view(), name="event-update"),
    path("<int:pk>/delete/", EventDeleteView.as_view(), name="event-delete"),
]
```

---

## 5. The Registrations App

This app links Users and Events together and enforces checking logic.

### 1. Define Model (`registrations/models.py`)
Stores registration status. We use a database unique key constraint `unique_together` to prevent database duplicate entries.
```python
from django.db import models
from django.conf import settings

class Registration(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [(STATUS_ACTIVE, "Active"), (STATUS_CANCELLED, "Cancelled")]

    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        db_table = "registrations"
        unique_together = ["event", "user"]

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.status})"
```

### 2. Write Business Validation Logic (`registrations/serializers.py`)
Validates user and capacity before updating database:
```python
from django.db import transaction
from rest_framework import serializers
from .models import Registration
from events.models import Event
from events.serializers import EventSerializer
from users.serializers import UserSerializer

class RegisterForEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()

    def validate_event_id(self, value):
        try:
            self._event = Event.objects.get(pk=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        event = self._event

        # 1. Prevent duplicate active registrations
        if Registration.objects.filter(event=event, user=user, status="ACTIVE").exists():
            raise serializers.ValidationError("You are already registered for this event.")

        # 2. Prevent overbooking with database locking
        with transaction.atomic():
            active_count = Registration.objects.select_for_update().filter(event=event, status="ACTIVE").count()
            if active_count >= event.capacity:
                raise serializers.ValidationError("Event capacity has been reached.")

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        event = self._event

        # Reactivate cancelled registration if it exists; otherwise create a new one
        registration, created = Registration.objects.get_or_create(
            event=event, user=user,
            defaults={"status": "ACTIVE"}
        )
        if not created and registration.status == "CANCELLED":
            registration.status = "ACTIVE"
            registration.save()
        return registration

class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "event", "user", "registered_at", "status"]
```

### 3. Create Views (`registrations/views.py`)
```python
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Registration
from .serializers import RegisterForEventSerializer, RegistrationSerializer

class RegisterForEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterForEventSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            registration = serializer.save()
            return Response({
                "message": "Registration successful.",
                "registration_id": registration.id,
                "status": registration.status
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)

class CancelRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            registration = Registration.objects.get(pk=pk, user=request.user)
        except Registration.DoesNotExist:
            return Response({"error": "Registration not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        if registration.status == "CANCELLED":
            return Response({"error": "Registration is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        registration.status = "CANCELLED"
        registration.save()
        return Response({"message": "Registration cancelled successfully."}, status=status.HTTP_200_OK)
```

### 4. Map Registration URLs (`registrations/urls.py`)
```python
from django.urls import path
from .views import RegisterForEventView, MyRegistrationsView, CancelRegistrationView

urlpatterns = [
    path("register/", RegisterForEventView.as_view(), name="register-for-event"),
    path("my/", MyRegistrationsView.as_view(), name="my-registrations"),
    path("<int:pk>/cancel/", CancelRegistrationView.as_view(), name="cancel-registration"),
]
```

---

## 5. Phase 5: Database Setup, Migrations & Launch

Now we connect the local code to the database engine.

### 1. Create a `.env` File
Create a new file named **`.env`** in the root project folder (next to `manage.py`):
```ini
SECRET_KEY=yoursecretkeyhere
DEBUG=True
DB_NAME=eventdb
DB_USER=postgres
DB_PASSWORD=Pyruvate#13
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 2. Configure Database
Launch PostgreSQL (pgAdmin or psql) and run:
```sql
CREATE DATABASE eventdb;
```

### 3. Create and Apply Migrations
Generate database tables by running:
```bash
python manage.py makemigrations users events registrations
python manage.py migrate
```

### 4. Create an Admin Account
```bash
python manage.py createsuperuser
```
Follow the prompts (Username: `admin`, Email: `admin@test.com`, Password: `adminpassword`).

### 5. Launch
```bash
python manage.py runserver
```

---

## 6. Testing Manual (Admin, Browser, and Postman)

Follow these validation paths locally:

### A. Testing using the Web Browser
Open your browser and navigate to these endpoints:

1.  **`/` (API Index)**: `http://localhost:8000/`
    *   *Expected result*: You should see a list of JSON urls and descriptions.
2.  **`/api/events/` (List Events)**: `http://localhost:8000/api/events/`
    *   *Expected result*: Displays an empty array `[]` in the browsable API framework.
3.  **`/api/auth/register/` (Registration Form)**: `http://localhost:8000/api/auth/register/`
    *   *Expected result*: Shows a HTML text-form at the bottom. Fill in credentials (email, username, password, password_confirm) and click **POST** to register a user.

---

### B. Testing using the Django Admin Panel
1.  Go to: `http://localhost:8000/admin/`
2.  Enter the credentials:
    *   **Email**: `admin@test.com`
    *   **Password**: `adminpassword`
3.  You can add Users, edit Event records, and view Registrations.

---

### C. Testing using Postman
Open Postman and follow these request steps:

#### 1. Register a new user
*   **Method**: `POST`
*   **URL**: `http://127.0.0.1:8000/api/auth/register/`
*   **Body**: `raw` -> `JSON`
*   **Payload**:
    ```json
    {
        "username": "organizer_one",
        "email": "organizer@test.com",
        "password": "password123",
        "password_confirm": "password123",
        "role": "ORGANIZER"
    }
    ```
*   **Expected Response**: `201 Created` containing a generated JWT `"access"` and `"refresh"` token. Copy the access token.

#### 2. Create an event (Requires Organizer Access)
*   **Method**: `POST`
*   **URL**: `http://127.0.0.1:8000/api/events/create/`
*   **Headers**: Add the Authorization header:
    *   **Key**: `Authorization`
    *   **Value**: `Bearer <Paste_Access_Token>`
*   **Body**: `raw` -> `JSON`
*   **Payload**:
    ```json
    {
        "name": "Global Tech Meeting",
        "description": "Annual technical showcase.",
        "date": "2026-12-01T10:00:00Z",
        "location": "Room 5B",
        "capacity": 2
    }
    ```
*   **Expected Response**: `201 Created` with a new event ID. Write down the ID (e.g. `1`).

#### 3. Log in as a User
First, register a normal user via the `/api/auth/register/` endpoint with `"role": "USER"`.
Log in to generate their user access token:
*   **Method**: `POST`
*   **URL**: `http://127.0.0.1:8000/api/auth/login/`
*   **Body**: `raw` -> `JSON`
*   **Payload**:
    ```json
    {
        "email": "user@test.com",
        "password": "password123"
    }
    ```
*   **Expected Response**: Copy the generated `"access"` token.

#### 4. Register for the Event
*   **Method**: `POST`
*   **URL**: `http://127.0.0.1:8000/api/registrations/register/`
*   **Headers**: 
    *   `Authorization`: `Bearer <Paste_User_Access_Token>`
*   **Body**: `raw` -> `JSON`
*   **Payload**:
    ```json
    {
        "event_id": 1
    }
    ```
*   **Expected Response**: `201 Created` confirming successful registration.

#### 5. Verify Capacity Validation (Optional Test)
Log in with a second user account and register for the same event (ID `1`). If you try to register a third user account for the same event, it will return:
```json
{
    "error": "Event capacity has been reached."
}
```
This confirms that the capacity rules are actively working.
