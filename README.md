# SupportFlow

A production-oriented **multi-tenant customer support and SLA management API** built with Django REST Framework.

SupportFlow enables organizations to manage customers, support tickets, teams, SLA policies, notifications, ratings, audit logs, analytics, and reports through a secure REST API.

## 🚀 Key Features

* 🔐 JWT Authentication
* 👤 Custom User Model
* 🏢 Multi-Tenant Organization Architecture
* 👥 Organization Membership & Role-Based Access Control
* 🎫 Customer Support Ticket Management
* 👨‍💼 Team & Agent Management
* 👤 Customer Management
* ⏱️ SLA Policy & Ticket SLA Tracking
* 🔔 Notifications
* ⭐ Ticket & Customer Ratings
* 📝 Internal & Public Ticket Comments
* 📋 Organization Audit Logs
* 📊 Analytics & Reporting
* 📈 Support & Ticket Statistics
* 🩺 Application Health Check
* 🪵 Application Logging
* 🐘 PostgreSQL Database
* 🐳 Docker & Docker Compose
* 🌐 Nginx Reverse Proxy
* 📚 Swagger / OpenAPI Documentation
* 🧪 Automated Test Suite
* 🏗️ Terraform Infrastructure Configuration

## 🏗️ Architecture

```text
                    Client
                      │
                      ▼
              ┌───────────────┐
              │     Nginx     │
              │ Reverse Proxy │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    Django     │
              │  REST API     │
              └───────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    PostgreSQL     JWT Auth    Application
                               Logging
```

## 🧩 Core Modules

| Module          | Responsibility                         |
| --------------- | -------------------------------------- |
| `account`       | Authentication, users and profiles     |
| `organizations` | Organizations, memberships and roles   |
| `teams`         | Teams and team members                 |
| `customers`     | Customer management                    |
| `tickets`       | Ticket and support workflow management |
| `sla`           | SLA policies and SLA tracking          |
| `notifications` | Organization notifications             |
| `ratings`       | Ticket/customer ratings                |
| `audit`         | Organization activity and audit logs   |
| `analytics`     | Support and ticket analytics           |
| `reports`       | Organization reports                   |

## 🔐 Authentication & Authorization

SupportFlow uses **JWT-based authentication** with role-based access control.

### Supported Roles

* **Owner**
* **Admin**
* **Agent**
* **Customer**

Access to organization resources is isolated using organization-level permissions.

Users can only access resources belonging to organizations they are authorized to access.

## 🎫 Ticket Management

The ticket system supports the core customer-support workflow:

* Create tickets
* Assign tickets to teams/agents
* Manage ticket status
* Track priorities
* Add comments
* Separate public and internal communication
* Apply SLA policies
* Track SLA status
* Collect ratings
* Record ticket-related activity

## ⏱️ SLA Management

SupportFlow includes SLA functionality for managing support response and resolution expectations.

SLA features include:

* SLA policies
* Ticket SLA tracking
* Response-time monitoring
* Resolution-time monitoring
* SLA status tracking
* Automated escalation logic

## 📊 Analytics & Reports

The API provides organization-level analytics and reporting for support operations.

Examples include:

* Ticket statistics
* Ticket status summaries
* Priority-based statistics
* Agent/team performance
* Customer support metrics
* Organization reports

## 📝 Audit Logging

Important organization activities are recorded through the audit system.

This provides visibility into actions performed inside an organization and helps with accountability and operational tracking.

## 🩺 Health Check

SupportFlow provides a lightweight health endpoint:

```http
GET /health/
```

Example response:

```json
{
    "status": "healthy",
    "database": "connected"
}
```

The endpoint verifies application availability and PostgreSQL connectivity.

## 🪵 Logging & Monitoring

Application logs are written to the container console, making them compatible with Docker logging.

Example:

```text
INFO | django.utils.autoreload | Watching for file changes
```

Docker logs can be viewed using:

```bash
docker compose logs web
```

Follow live logs:

```bash
docker compose logs -f web
```

Database logs:

```bash
docker compose logs db
```

## 🛠️ Tech Stack

### Backend

* Python
* Django
* Django REST Framework

### Authentication

* Simple JWT

### Database

* PostgreSQL

### API Documentation

* drf-spectacular
* Swagger UI
* ReDoc

### Infrastructure

* Docker
* Docker Compose
* Nginx
* Terraform

### Testing

* Django Test Framework

## 📁 Project Structure

```text
SupportFlow/
│
├── account/
├── organizations/
├── teams/
├── customers/
├── tickets/
├── sla/
├── notifications/
├── ratings/
├── audit/
├── analytics/
├── reports/
│
├── infra/
│   └── terraform/
│
├── nginx/
│
├── src/
│   ├── settings.py
│   ├── urls.py
│   ├── health.py
│   ├── wsgi.py
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
├── manage.py
└── README.md
```

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Almas-Web/supportflow.git
cd supportflow
```

### 2. Create environment variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=supportflow
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

LOG_LEVEL=INFO
```

Add the required email configuration if email functionality is enabled.

> Never commit your real `.env` file or secret credentials to GitHub.

### 3. Start Docker services

```bash
docker compose up -d --build
```

Check the containers:

```bash
docker compose ps
```

Expected services:

```text
supportflow_db
supportflow_web
supportflow_nginx
```

### 4. Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## 📚 API Documentation

After starting the application:

### Swagger UI

```text
http://localhost:8000/api/docs/
```

### ReDoc

```text
http://localhost:8000/api/redoc/
```

### OpenAPI Schema

```text
http://localhost:8000/api/schema/
```

## 🩺 Health Check

```text
http://localhost:8000/health/
```

Expected:

```json
{
    "status": "healthy",
    "database": "connected"
}
```

## 🧪 Testing

Run the complete test suite:

```bash
docker compose exec web python manage.py test
```

Current test suite:

```text
206 tests
206 passed
```

Run Django system checks:

```bash
docker compose exec web python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

## 🐳 Docker Services

The project uses three main containers:

```text
┌─────────────────────┐
│       Nginx         │
│       :8000         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Django         │
│     Gunicorn        │
│       :8000         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     PostgreSQL      │
│       :5432         │
└─────────────────────┘
```

PostgreSQL data is stored in a Docker named volume for persistence.

## 🏗️ Infrastructure

Terraform configuration is included under:

```text
infra/terraform/
```

The infrastructure configuration is kept separate from the application code to maintain a clean project structure.

## 🔒 Security

Production-oriented security configurations include:

* Environment-based secret management
* JWT authentication
* Role-based permissions
* Organization-level data isolation
* Secure cookies in production
* HTTPS redirect in production
* HSTS
* `X-Frame-Options`
* Content-type sniffing protection
* Referrer policy
* Password validation

## 🎯 Project Goals

SupportFlow was built to demonstrate practical backend engineering concepts including:

* REST API development
* Multi-tenant SaaS architecture
* Authentication & authorization
* Role-based access control
* Database design
* Business logic
* SLA management
* Audit logging
* Analytics
* Automated testing
* Containerization
* Production-oriented configuration

## 📌 Project Status

**Status: Feature-complete and tested**

* ✅ Core backend implemented
* ✅ Authentication & authorization
* ✅ Multi-tenancy
* ✅ Ticket management
* ✅ SLA management
* ✅ Notifications
* ✅ Ratings
* ✅ Audit logging
* ✅ Analytics
* ✅ Reports
* ✅ Logging
* ✅ Health monitoring
* ✅ Docker setup
* ✅ Nginx configuration
* ✅ Terraform infrastructure configuration
* ✅ 206 automated tests passing
* ✅ Django system checks passing

## 👨‍💻 Author

**Almas Hossen**

Python Backend Developer

GitHub: https://github.com/Almas-Web

---

⭐ If you find this project useful, consider giving the repository a star.
