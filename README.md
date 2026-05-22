# Django Backend Project

A Django REST Framework backend application for managing users, events, and registrations.

## Project Structure

```
backend/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── test_api.py              # API tests
├── config/                  # Django configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI application
│   └── __init__.py
├── users/                   # User management app
│   ├── models.py            # User models
│   ├── views.py             # User views/viewsets
│   ├── serializers.py       # User serializers
│   ├── urls.py              # User URL routes
│   ├── admin.py             # User admin configuration
│   ├── permissions.py       # Permission classes
│   ├── managers.py          # Custom managers
│   ├── constants.py         # User constants
│   ├── apps.py              # App configuration
│   ├── migrations/
│   └── __init__.py
├── events/                  # Event management app
│   ├── models.py            # Event models
│   ├── views.py             # Event views/viewsets
│   ├── serializers.py       # Event serializers
│   ├── urls.py              # Event URL routes
│   ├── admin.py             # Event admin configuration
│   ├── permissions.py       # Permission classes
│   ├── apps.py              # App configuration
│   ├── migrations/
│   └── __init__.py
└── registrations/           # Registration management app
    ├── models.py            # Registration models
    ├── views.py             # Registration views/viewsets
    ├── serializers.py       # Registration serializers
    ├── urls.py              # Registration URL routes
    ├── admin.py             # Registration admin configuration
    ├── apps.py              # App configuration
    ├── migrations/
    └── __init__.py
```

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Update Django settings** (if needed)
   - Modify `config/settings.py` for your environment
   - Configure database settings
   - Set secret key and allowed hosts

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

## Running the Project

1. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`

2. **Access the admin panel**
   - Navigate to `http://127.0.0.1:8000/admin/`
   - Log in with your superuser credentials

## API Endpoints

The project provides REST API endpoints for:

- **Users**: `/api/users/` - User management
- **Events**: `/api/events/` - Event management
- **Registrations**: `/api/registrations/` - Registration management

## Testing

Run tests using the provided test file:
```bash
python test_api.py
```

Or use Django's test runner:
```bash
python manage.py test
```

## Dependencies

Key dependencies are listed in `requirements.txt`:
- Django
- Django REST Framework
- Additional packages as specified

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Development

- Follow Django best practices and conventions
- Use Django Admin (`/admin/`) for data management during development
- API endpoints follow REST conventions

## Troubleshooting

- **Port already in use**: Change the port with `python manage.py runserver 8001`
- **Migration errors**: Ensure all migrations are applied with `python manage.py migrate`
- **Import errors**: Verify the virtual environment is activated and all dependencies are installed

## License

[Add your license information here]

## Support

For issues or questions, please contact the development team.
