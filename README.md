# MisalAI Blog

A Django-based blog platform with REST API support, PostgreSQL database, and Docker deployment configuration.

![img.png](img.png)

## Technologies Used

- Python 3.11
- Django 5.1.6
- PostgreSQL 15
- Django REST Framework
- Nginx 1.25
- Docker & Docker Compose
- Gunicorn

## Features

- User Authentication System
- Blog Post Management
- Category and Tag System
- REST API Endpoints
- Media File Handling
- Admin Interface
- Search Functionality
- Author-specific Post Views

## Project Structure

```
mislai_blog/
├── accounts/           # Custom user authentication app
├── blog/              # Main blog application
├── mislai_blog/       # Project configuration
├── nginx/            # Nginx configuration
├── static/           # Static files
├── mediafiles/       # User uploaded media
├── templates/        # HTML templates
└── requirements.txt  # Python dependencies
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.11 (for local development)
- PostgreSQL 15

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432
```

### Docker Deployment

1. Build and start the containers:
```bash
docker-compose up --build
```

2. The application will be available at:
   - Main application: http://localhost:80
   - Admin interface: http://localhost:80/admin

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- Blog Posts: `/api/`
- Authentication: `/api/auth/`
- Admin Interface: `/admin/`
- User Accounts: `/accounts/`

## Security Features

- Token Authentication
- Session Authentication
- CSRF Protection
- Secure Password Validation
- Custom User Model

## Database Configuration

The project uses PostgreSQL with the following configuration:
- Engine: django.db.backends.postgresql
- Host: Configured via environment variable
- Port: Configured via environment variable
- Database Name: Configured via environment variable
- User & Password: Configured via environment variables

## Media and Static Files

- Static files are served from `/static/`
- Media files are served from `/media/`
- Files are stored in Docker volumes for persistence

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]