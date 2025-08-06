# Astrology API Backend

A comprehensive astrology API built with FastAPI, PostgreSQL, and the Kerykeion library.

## Features

### Core Astrology Features
- ✅ Natal Chart Generation (JSON & SVG)
- ✅ Full Natal Reports
- ✅ Synastry (Relationship) Analysis
- ✅ Composite Charts
- ✅ Relationship Compatibility Scoring
- ✅ Daily Transit Analysis

### User Management
- ✅ User Registration & Authentication
- ✅ Password Hashing with bcrypt
- ✅ User Profiles with Birth Data
- ✅ Premium User System

### Chart Management
- ✅ Save Multiple Charts per User
- ✅ Chart History & Analysis
- ✅ Chart Sharing & Export

### Advanced Features
- ✅ Gamification System (XP, Levels, Tasks)
- ✅ User Event Tracking
- ✅ Notification System
- ✅ AI Chatbot for Chart Analysis
- ✅ Article Management

## Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts and profiles
- **charts**: Natal charts and birth data
- **chart_analyses**: Analysis reports and interpretations
- **composite_charts**: Relationship charts
- **daily_transits**: Daily transit analysis
- **subscriptions**: Premium subscription management
- **user_progress**: Gamification data
- **notifications**: User notifications
- **chatbots**: AI chat sessions
- **articles**: Content management

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd mini-astro/app
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**
```bash
# Create database
createdb astrology_db

# Or use Docker
docker run --name postgres-astro -e POSTGRES_PASSWORD=password -e POSTGRES_DB=astrology_db -p 5432:5432 -d postgres:13
```

4. **Configure environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your database credentials
SQLALCHEMY_DATABASE_URL=postgresql://user:password@localhost/astrology_db
SECRET_KEY=your-secret-key
```

5. **Run the application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/v1/users/` - Register new user
- `POST /api/v1/users/login` - User login

### Astrology
- `POST /api/v1/astro/chart-json` - Generate natal chart (JSON)
- `POST /api/v1/astro/chart-svg` - Generate natal chart (SVG)
- `POST /api/v1/astro/report` - Full natal report
- `POST /api/v1/astro/synastry` - Relationship analysis
- `POST /api/v1/astro/relationship-score` - Compatibility score
- `POST /api/v1/astro/composite` - Composite chart

### Chart Management
- `POST /api/v1/astro/charts/` - Create new chart
- `GET /api/v1/astro/charts/` - Get user charts
- `GET /api/v1/astro/charts/{chart_id}` - Get specific chart

## Development

### Project Structure
```
app/
├── api/v1/           # API endpoints
├── core/             # Configuration & dependencies
├── db/               # Database models & session
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── services/         # Business logic
└── main.py          # FastAPI application
```

### Database Migrations
```bash
# Initialize database tables
python -c "from app.db.init_db import init_db; init_db()"
```

### Testing
```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

### Docker
```bash
# Build image
docker build -t astrology-api .

# Run container
docker run -p 8000:8000 astrology-api
```

### Production
- Use PostgreSQL in production
- Set proper SECRET_KEY
- Configure CORS origins
- Use HTTPS
- Set up proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 