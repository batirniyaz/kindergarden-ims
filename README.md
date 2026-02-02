# 🏫 Kindergarten IMS - Inventory Management System

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)

**A comprehensive backend solution for managing kindergarten meal inventory, ingredient tracking, and portion control with real-time monitoring capabilities.**

[Features](#-features) •
[Architecture](#-architecture) •
[Getting Started](#-getting-started) •
[API Documentation](#-api-documentation) •
[Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
  - [Running the Application](#running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Core Modules](#-core-modules)
- [Background Tasks](#-background-tasks)
- [Real-time Features](#-real-time-features)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

**Kindergarten IMS** is a robust backend system designed to streamline inventory management for kindergartens and similar institutions. The system provides comprehensive tracking of ingredients, meal preparation, delivery management, and portion estimation — all critical for ensuring children receive proper nutrition while minimizing waste and preventing misuse.

### 🎯 Key Objectives

- **Efficient Ingredient Tracking**: Monitor ingredient stock levels in real-time
- **Meal Management**: Create and manage meal recipes with ingredient associations
- **Delivery Logging**: Track incoming ingredient deliveries with accountability
- **Portion Estimation**: Calculate available meal portions based on current inventory
- **Misuse Detection**: Automated monthly analysis to flag discrepancies in ingredient usage
- **Real-time Notifications**: WebSocket-based alerts for critical events
- **Comprehensive Reporting**: Detailed analytics on ingredient usage and meal statistics

---

## ✨ Features

### 🍽️ Meal & Ingredient Management
- Create, read, update, and delete meals and ingredients
- Define meal recipes with precise ingredient quantities
- Track ingredient stock levels automatically

### 📦 Delivery Management
- Log ingredient deliveries with user accountability
- Automatic stock level updates upon delivery
- Historical delivery tracking

### 📊 Portion Estimation
- Real-time calculation of available meal portions
- WebSocket streaming for live portion updates
- Based on current ingredient availability

### 🔔 Smart Notifications
- Real-time WebSocket alerts
- Monthly discrepancy notifications
- Persistent notification storage

### 📈 Advanced Reporting
- **Ingredient Usage Reports**: Track consumption over time (daily, weekly, monthly)
- **Monthly Summary Reports**: Comprehensive analysis with misuse detection
- **Ingredient Analysis**: Detailed breakdown of ingredient usage patterns

### 👥 User Management & Security
- Role-based access control (Admin, Manager, Cook)
- JWT-based authentication
- Token blacklisting for secure logout
- Login activity tracking

### 📝 Audit Trail
- Complete action logging
- Database change tracking
- Request/response monitoring

---

## 🏗️ Architecture

The application follows a modular, layered architecture designed for scalability and maintainability.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENTS                                       │
│                    (Web App / Mobile App / API Consumers)                       │
└───────────────────────────────────┬────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │         HTTP / WebSocket       │
                    └───────────────┬───────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────────┐
│                              FASTAPI SERVER                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           MIDDLEWARE LAYER                               │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │   │
│  │  │  CORS Handler   │  │ Logging Middleware│  │  Request/Response Log  │  │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                             API LAYER                                    │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │   │
│  │  │   Auth API   │  │ Ingredient │  │  Meal API  │  │  Delivery API   │  │   │
│  │  │   /login     │  │    API     │  │   /meal    │  │   /delivery     │  │   │
│  │  │   /logout    │  │/ingredient │  │            │  │                 │  │   │
│  │  └──────────────┘  └────────────┘  └────────────┘  └─────────────────┘  │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │   │
│  │  │ Serve Meal   │  │   Report   │  │   Celery   │  │   WebSocket     │  │   │
│  │  │    API       │  │    API     │  │    API     │  │  /ws/portion    │  │   │
│  │  │ /serve-meal  │  │  /report   │  │  /celery   │  │  /ws/notification│ │   │
│  │  └──────────────┘  └────────────┘  └────────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          BUSINESS LOGIC LAYER                            │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │   │
│  │  │   Auth &     │  │   CRUD     │  │  Portion   │  │    Reports      │  │   │
│  │  │ JWT Handling │  │ Operations │  │ Estimation │  │   Generation    │  │   │
│  │  └──────────────┘  └────────────┘  └────────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           DATA ACCESS LAYER                              │   │
│  │                     SQLAlchemy Async ORM + Pydantic                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│                   │   │                   │   │                   │
│    PostgreSQL     │   │      Redis        │   │   Celery Worker   │
│    (Primary DB)   │   │  (Message Broker) │   │  (Task Executor)  │
│                   │   │                   │   │                   │
│  • Users          │   │  • Task Queue     │   │  • Scheduled Jobs │
│  • Ingredients    │   │  • Result Backend │   │  • Log Cleanup    │
│  • Meals          │   │                   │   │  • Monthly Reports│
│  • Deliveries     │   │                   │   │                   │
│  • Servings       │   │                   │   │                   │
│  • Logs           │   │                   │   │                   │
│                   │   │                   │   │                   │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

### 📐 Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INGREDIENT DELIVERY FLOW                            │
│                                                                              │
│   📦 Delivery     ──►    📝 Log Entry     ──►    📊 Stock Update           │
│   Received              Created                  Ingredient.weight          │
│                              │                         │                     │
│                              └─────────────────────────┼─────────────────┐  │
│                                                        │                 │  │
│                                                        ▼                 ▼  │
│                                              ┌─────────────┐   ┌──────────┐ │
│                                              │   Portion   │   │ WebSocket│ │
│                                              │ Recalculate │──►│ Broadcast│ │
│                                              └─────────────┘   └──────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            MEAL SERVING FLOW                                 │
│                                                                              │
│   🍽️ Meal Served   ──►    📝 Serving Log    ──►    📊 Stock Deduction      │
│                                  │                         │                 │
│                                  │                         │                 │
│                                  ▼                         ▼                 │
│                         ┌──────────────┐         ┌─────────────────┐        │
│                         │  Action Log  │         │ Portion Update  │        │
│                         │   Created    │         │   Broadcast     │        │
│                         └──────────────┘         └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         MONTHLY REPORT FLOW                                  │
│                                                                              │
│   ⏰ Celery Beat    ──►   📊 Data Analysis   ──►   🔔 Notification          │
│   (1st of Month)              │                         │                    │
│                               │                         │                    │
│                               ▼                         ▼                    │
│                      ┌─────────────────┐       ┌───────────────────┐        │
│                      │ Compare Served  │       │ WebSocket Alert   │        │
│                      │  vs Possible    │       │ (if threshold     │        │
│                      │   Portions      │       │   exceeded)       │        │
│                      └─────────────────┘       └───────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115.x | High-performance async web framework |
| **Python** | 3.11+ | Programming language |
| **Uvicorn** | Latest | ASGI server |

### Database & ORM

| Technology | Purpose |
|------------|---------|
| **PostgreSQL** | Primary relational database |
| **SQLAlchemy 2.0** | Async ORM with native asyncio support |
| **asyncpg** | High-performance PostgreSQL driver |
| **Alembic** | Database migrations |

### Authentication & Security

| Technology | Purpose |
|------------|---------|
| **PyJWT** | JSON Web Token handling |
| **bcrypt** | Password hashing |
| **python-dotenv** | Environment variable management |

### Task Queue & Scheduling

| Technology | Purpose |
|------------|---------|
| **Celery** | Distributed task queue |
| **Redis** | Message broker & result backend |
| **Celery Beat** | Periodic task scheduling |

### Data Validation

| Technology | Purpose |
|------------|---------|
| **Pydantic** | Data validation and serialization |
| **email-validator** | Email validation |

### Other

| Technology | Purpose |
|------------|---------|
| **WebSockets** | Real-time bidirectional communication |
| **pytz** | Timezone handling (Asia/Tashkent) |
| **Faker** | Test data generation |

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Minimum Version | Download Link |
|-------------|-----------------|---------------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| PostgreSQL | 14+ | [postgresql.org](https://www.postgresql.org/download/) |
| Redis | 6+ | [redis.io](https://redis.io/download/) |
| Git | Latest | [git-scm.com](https://git-scm.com/downloads) |

### Installation

#### Windows (PowerShell / CMD)

```powershell
# 1. Clone the repository
git clone https://github.com/your-username/kindergarden-ims.git
cd kindergarden-ims

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# PowerShell:
.\.venv\Scripts\Activate.ps1
# CMD:
.\.venv\Scripts\activate.bat

# 4. Install dependencies
pip install -r reqs.txt
```

#### macOS / Linux (Bash)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/kindergarden-ims.git
cd kindergarden-ims

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r reqs.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# ═══════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════
DB_USER=postgres
DB_PASS=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kindergarden_ims

# ═══════════════════════════════════════════════════════════
# JWT CONFIGURATION
# ═══════════════════════════════════════════════════════════
SECRET=your_super_secret_jwt_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> ⚠️ **Security Note**: Never commit your `.env` file to version control. Add it to `.gitignore`.

### Database Setup

#### 1. Create the PostgreSQL Database

```sql
-- Connect to PostgreSQL and create the database
CREATE DATABASE kindergarden_ims;
```

#### 2. Run Migrations

```bash
# Apply all migrations
alembic upgrade head
```

### Running the Application

#### Start the FastAPI Server

```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

#### Start Celery Worker (Required for background tasks)

```bash
# In a new terminal window
celery -A app.celery.celery_app worker --loglevel=info
```

#### Start Celery Beat (Required for scheduled tasks)

```bash
# In another terminal window
celery -A app.celery.celery_app beat --loglevel=info
```

> 💡 **Tip**: For production, consider using a process manager like Supervisor or systemd.

---

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

| Documentation | URL |
|---------------|-----|
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

### API Endpoints Overview

#### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/login` | User login, returns JWT token |
| `POST` | `/logout` | Invalidate current token |
| `GET` | `/me/` | Get current user profile |
| `GET` | `/login_info/` | Get login history (Admin) |
| `GET` | `/logging` | Get action logs (Admin) |

#### 🥕 Ingredients
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ingredient/` | List all ingredients |
| `POST` | `/ingredient/` | Create new ingredient |
| `GET` | `/ingredient/{id}` | Get ingredient by ID |
| `DELETE` | `/ingredient/{id}` | Delete ingredient |

#### 🍲 Meals
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/meal/` | List all meals |
| `POST` | `/meal/` | Create new meal |
| `GET` | `/meal/{id}` | Get meal by ID |
| `DELETE` | `/meal/{id}` | Delete meal |

#### 🔗 Meal-Ingredient Associations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/meal-ingredient/` | List all associations |
| `POST` | `/meal-ingredient/` | Create association |
| `DELETE` | `/meal-ingredient/{meal_id}/{ingredient_id}` | Remove association |

#### 📦 Deliveries
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/delivery/` | List all deliveries |
| `POST` | `/delivery/` | Log new delivery |
| `GET` | `/delivery/{id}` | Get delivery by ID |

#### 🍽️ Meal Servings
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/serve-meal/` | List all servings |
| `POST` | `/serve-meal/` | Log meal serving |
| `GET` | `/serve-meal/{id}` | Get serving by ID |

#### 📊 Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/report/ingredient-usage/` | Ingredient usage over time |
| `GET` | `/report/monthly-summary/` | Monthly summary with misuse detection |
| `GET` | `/report/ingredient-analysis/` | Detailed ingredient analysis |

#### 🔌 WebSocket Endpoints
| Protocol | Endpoint | Description |
|----------|----------|-------------|
| `WS` | `/ws/portion/stream` | Real-time portion updates |
| `WS` | `/ws/notification/alerts` | Real-time alerts/notifications |

---

## 📁 Project Structure

```
kindergarden-ims/
│
├── 📄 alembic.ini                 # Alembic configuration
├── 📄 reqs.txt                    # Python dependencies
├── 📄 README.md                   # This file
│
├── 📂 alembic/                    # Database migrations
│   ├── env.py                     # Alembic environment config
│   ├── script.py.mako             # Migration template
│   └── 📂 versions/               # Migration files
│       ├── 4125a26bb55f_initial_commit.py
│       ├── d36b33379dc8_created_table_changelog.py
│       └── ...
│
└── 📂 app/                        # Main application package
    │
    ├── 📄 __init__.py             # Router aggregation
    ├── 📄 config.py               # Application configuration
    ├── 📄 main.py                 # FastAPI application entry point
    │
    ├── 📂 auth/                   # Authentication module
    │   ├── api.py                 # Auth endpoints
    │   ├── model.py               # User, LoginInfo, TokenBlacklist models
    │   ├── schema.py              # Pydantic schemas
    │   ├── util.py                # JWT utilities, auth helpers
    │   └── superuser.py           # Superuser creation
    │
    ├── 📂 celery/                 # Background tasks
    │   ├── celery_app.py          # Celery configuration
    │   ├── api.py                 # Celery-related endpoints
    │   └── tasks.py               # Task definitions
    │
    ├── 📂 changes/                # Audit trail & change tracking
    │   ├── funcs.py               # Event listeners, logging functions
    │   ├── model.py               # ChangeLog model
    │   └── track_models.py        # Model registration
    │
    ├── 📂 db/                     # Database configuration
    │   ├── base.py                # SQLAlchemy Base, table creation
    │   ├── db.py                  # Engine & session factory
    │   └── get_db.py              # Dependency injection
    │
    ├── 📂 endpoints/              # API endpoint handlers
    │   ├── delivery.py            # Delivery endpoints
    │   ├── meal_ingredient.py     # Meal-Ingredient association endpoints
    │   ├── notification.py        # WebSocket notifications
    │   ├── portion_estimation.py  # WebSocket portions
    │   └── serve_meal.py          # Meal serving endpoints
    │
    ├── 📂 functions/              # Business logic
    │   ├── delivery.py            # Delivery logic
    │   ├── meal_ingredient.py     # Association logic
    │   ├── notification.py        # Notification logic
    │   ├── portion_estimation.py  # Portion calculation logic
    │   └── serve_meal.py          # Serving logic
    │
    ├── 📂 ingredient/             # Ingredient module
    │   ├── api.py                 # Ingredient endpoints
    │   ├── crud.py                # CRUD operations
    │   └── schema.py              # Pydantic schemas
    │
    ├── 📂 meal/                   # Meal module
    │   ├── api.py                 # Meal endpoints
    │   ├── crud.py                # CRUD operations
    │   └── schema.py              # Pydantic schemas
    │
    ├── 📂 middleware/             # Custom middleware
    │   └── login_middleware.py    # Request logging, user context
    │
    ├── 📂 models/                 # SQLAlchemy models
    │   ├── action_log.py          # ActionLog model
    │   ├── delivery.py            # IngredientDelivery model
    │   ├── meal_ingredient.py     # Meal, Ingredient, MealIngredient models
    │   ├── notification.py        # Notification model
    │   ├── portion_estimation.py  # PortionEstimation model
    │   └── serve_meal.py          # MealServing model
    │
    ├── 📂 reports/                # Reporting module
    │   ├── __init__.py            # Report router aggregation
    │   ├── ingredient_analysis.py # Ingredient breakdown reports
    │   ├── ingredient_usage.py    # Usage over time reports
    │   └── monthly_summary.py     # Monthly summary with misuse detection
    │
    └── 📂 schemas/                # Shared Pydantic schemas
        ├── delivery.py
        ├── meal_ingredient.py
        ├── serve_meal.py
        └── util.py
```

---

## 🧩 Core Modules

### 🔐 Authentication (`app/auth/`)

The authentication system provides:
- **JWT-based authentication** with configurable expiration
- **Role-based access control**: Admin, Manager, Cook
- **Token blacklisting** for secure logout
- **Login history tracking** for audit purposes

```python
# User Roles
class UserRole(Enum):
    COOK = 'cook'       # Can serve meals, view ingredients
    ADMIN = 'admin'     # Full access, user management
    MANAGER = 'manager' # Reports, deliveries, oversight
```

### 🍽️ Meal Management (`app/meal/`, `app/ingredient/`)

- **Ingredients**: Track available ingredients with current stock (weight in grams)
- **Meals**: Define meals with names and associated ingredients
- **Meal-Ingredient Association**: Many-to-many relationship with weight per ingredient per meal

### 📦 Delivery System (`app/endpoints/delivery.py`)

When a delivery is logged:
1. The ingredient's total weight is updated
2. Portion estimations are recalculated
3. Connected WebSocket clients receive live updates

### 📊 Portion Estimation (`app/functions/portion_estimation.py`)

Calculates available portions based on:
- Current ingredient stock levels
- Ingredient requirements per meal
- The limiting ingredient determines maximum portions

```
Portion Count = MIN(ingredient_stock / required_per_meal) for each ingredient
```

### 📈 Reporting System (`app/reports/`)

Three comprehensive report types:

1. **Ingredient Usage** (`/report/ingredient-usage/`)
   - Tracks consumption and deliveries over time
   - Grouping by day, week, or month
   
2. **Monthly Summary** (`/report/monthly-summary/`)
   - Per-meal analysis of portions served vs. possible
   - Automatic misuse detection with configurable threshold
   
3. **Ingredient Analysis** (`/report/ingredient-analysis/`)
   - Detailed breakdown for a specific month

---

## ⏰ Background Tasks

### Celery Configuration

The application uses Celery with Redis for:

| Task | Schedule | Description |
|------|----------|-------------|
| `delete_old_logs` | Daily at midnight | Removes action logs older than 30 days |
| `monthly_summary` | 1st of month, 2:00 AM | Generates monthly report & triggers alerts |

### Starting Background Services

```bash
# Terminal 1: Redis (if not running as service)
redis-server

# Terminal 2: Celery Worker
celery -A app.celery.celery_app worker --loglevel=info

# Terminal 3: Celery Beat (Scheduler)
celery -A app.celery.celery_app beat --loglevel=info
```

---

## 🔌 Real-time Features

### WebSocket Endpoints

#### Portion Estimation Stream
```javascript
// Connect to receive live portion updates
const ws = new WebSocket('ws://localhost:8000/ws/portion/stream');

ws.onmessage = (event) => {
    const portions = JSON.parse(event.data);
    // [{ meal_id: 1, meal_name: "Soup", portion_count: 25 }, ...]
};
```

#### Notification Alerts
```javascript
// Connect to receive real-time alerts
const ws = new WebSocket('ws://localhost:8000/ws/notification/alerts');

ws.onmessage = (event) => {
    const alert = JSON.parse(event.data);
    // { type: 'monthly_discrepancy', message: '...', ... }
};
```

---

## 🧪 Development

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description_of_changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Creating Test Data

The project includes Faker for generating test data. You can extend this for development purposes.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for public functions and classes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Author

**Muratbaev Batirniyaz**

---

<div align="center">

**Made with ❤️ for kindergartens everywhere**

⭐ Star this repository if you find it helpful!

</div>

