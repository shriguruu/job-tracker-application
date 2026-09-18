# Job Tracker Application

A full-stack, production-grade Job Tracker Application engineered according to the **Technical Specification (v1)**. Designed to streamline career management by tracking job applications across hiring stages, managing reusable resumes in AWS S3, and providing multi-tenant data isolation and security.

---

## 1. Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, Pydantic v2 |
| **ORM & Migrations** | SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16 (Local & AWS RDS) |
| **Authentication** | JWT (HS256, 24h expiry, no refresh flow) |
| **Password Security** | Bcrypt hashing (salted, plaintext never persisted) |
| **File Storage** | AWS S3 with on-demand pre-signed download URLs (PDF only, max 5MB) |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons, Axios |
| **Containerization** | Docker, Docker Compose, Nginx |

---

## 2. Architecture Overview

```
                           +------------------------+
                           |  React Frontend (SPA)  |
                           |   (Vite + Tailwind)    |
                           +-----------+------------+
                                       |
                   HTTP Requests / JWT | Authorization: Bearer <token>
                                       v
                           +------------------------+
                           |    Nginx Web Server    |
                           |   (Reverse Proxy)      |
                           +-----------+------------+
                                       |
                                /api/v1/*
                                       v
                      +----------------------------------+
                      |     FastAPI Backend Service      |
                      |   - Auth / JWT Verification      |
                      |   - Tenant Isolation Filter      |
                      |   - Input / File Validation      |
                      +--------+----------------+--------+
                               |                |
                SQLAlchemy ORM |                | Boto3 S3 Client (IAM Role)
                               v                v
                    +--------------------+   +-------------------+
                    |   PostgreSQL DB    |   |   AWS S3 Bucket   |
                    | (Users, Resumes,   |   | (Uploaded PDFs)   |
                    |  Applications)     |   +-------------------+
                    +--------------------+
```

### Entity Relationship Diagram

```
users (1) ──────< (many) resumes
users (1) ──────< (many) applications
resumes (1) ────< (many) applications        [nullable FK: ON DELETE SET NULL]
```

---

## 3. Database Schema

### `users`
- `user_id`: UUID (Primary Key)
- `user_name`: VARCHAR(100), NOT NULL
- `email`: VARCHAR(255), NOT NULL, UNIQUE (stored lowercased)
- `password_hash`: VARCHAR(255), NOT NULL
- `phone_number`: VARCHAR(20), NULL
- `created_at`: TIMESTAMPTZ, default `now()`
- `updated_at`: TIMESTAMPTZ, default `now()`

### `resumes`
- `resume_id`: UUID (Primary Key)
- `user_id`: UUID (FK → `users.user_id`, ON DELETE CASCADE)
- `resume_name`: VARCHAR(150), NOT NULL
- `resume_key`: VARCHAR(500), NOT NULL (S3 object key: `resumes/{user_id}/{resume_id}.pdf`)
- `created_at`: TIMESTAMPTZ, default `now()`
- `updated_at`: TIMESTAMPTZ, default `now()`

### `applications`
- `application_id`: UUID (Primary Key)
- `user_id`: UUID (FK → `users.user_id`, ON DELETE CASCADE)
- `resume_id`: UUID (FK → `resumes.resume_id`, NULL, ON DELETE SET NULL)
- `company_name`: VARCHAR(150), NOT NULL
- `role_name`: VARCHAR(150), NOT NULL
- `ctc_amount`: NUMERIC(12,2), NULL
- `ctc_currency`: VARCHAR(3), default `'INR'`
- `status`: ENUM (`applied`, `oa`, `interview`, `offer`, `rejected`, `withdrawn`), default `'applied'`
- `job_description_url`: TEXT, NULL
- `notes`: TEXT, NULL
- `created_at`: TIMESTAMPTZ, default `now()`
- `updated_at`: TIMESTAMPTZ, default `now()`

---

## 4. API Endpoints Contract (`/api/v1`)

### Authentication
- `POST /api/v1/auth/signup` — Register new user, hashes password, returns `201` `{ user_id, token }`.
- `POST /api/v1/auth/login` — Verifies email and password, returns `200` `{ user_id, token }`.
- `GET /api/v1/auth/me` — Returns profile of the authenticated user.

### Applications
- `GET /api/v1/applications` — List current user's applications (supports query parameters: `status`, `page`, `page_size`).
- `POST /api/v1/applications` — Create a job application (validates resume ownership if attached).
- `GET /api/v1/applications/{id}` — Fetch application detail.
- `PUT /api/v1/applications/{id}` — Update application fields or change status.
- `DELETE /api/v1/applications/{id}` — Delete application (`204 No Content`).

### Resumes
- `GET /api/v1/resumes` — List current user's resumes.
- `POST /api/v1/resumes` — Multipart form upload (`resume_name`, `file`). Validates PDF MIME type and ≤ 5MB limit. Streams to S3 before DB insertion. Returns `201` `{ resume_id, resume_name }`.
- `GET /api/v1/resumes/{id}/download-url` — Generates short-lived (5 min) pre-signed S3 download URL.
- `DELETE /api/v1/resumes/{id}` — Deletes S3 object and database row. Applications referencing it have `resume_id` set to `NULL` (`204 No Content`).

### Uniform Error Response Format
All error responses adhere strictly to the technical specification:
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Human-readable message"
  }
}
```

---

## 5. Quick Start (Local Development)

### Option A: Using Docker Compose (Recommended)
Prerequisites: Docker and Docker Compose installed.

1. **Clone the repository**:
   ```bash
   git clone <repo_url>
   cd job-tracker-application
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - **Frontend UI**: [http://localhost](http://localhost)
   - **Backend API & Swagger Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
   - **Health check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option B: Running Manually Without Docker

#### 1. Backend Setup
```bash
cd Backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run database migrations (or let FastAPI auto-create tables on startup)
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 6. Running Automated Tests

A comprehensive test suite covers authentication, tenant data isolation, file upload validation, S3 download URL signing, application CRUD, and standard error shapes:

```bash
cd Backend
.venv\Scripts\python -m pytest -v
```

Output:
```
tests/test_applications.py::test_create_application_success PASSED
tests/test_applications.py::test_applications_user_isolation PASSED
tests/test_applications.py::test_update_and_delete_application PASSED
tests/test_applications.py::test_cannot_attach_other_users_resume PASSED
tests/test_auth.py::test_signup_success PASSED
tests/test_auth.py::test_signup_duplicate_email PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_invalid_credentials PASSED
tests/test_auth.py::test_get_current_user_profile PASSED
tests/test_error_shape.py::test_400_validation_error_shape PASSED
tests/test_error_shape.py::test_401_unauthorized_error_shape PASSED
tests/test_error_shape.py::test_404_not_found_error_shape PASSED
tests/test_error_shape.py::test_409_conflict_error_shape PASSED
tests/test_resumes.py::test_upload_resume_success PASSED
tests/test_resumes.py::test_upload_resume_invalid_file_type PASSED
tests/test_resumes.py::test_upload_resume_empty_file PASSED
tests/test_resumes.py::test_resume_presigned_download_url PASSED
tests/test_resumes.py::test_delete_resume_and_set_null_on_application PASSED
======================= 18 passed, 2 warnings in 4.50s ========================
```

---

## 7. AWS Deployment Guide

The application is cloud-native and designed to run identically between local development and AWS infrastructure:

### 1. Database (AWS RDS PostgreSQL)
- Create an Amazon RDS PostgreSQL 16 instance inside your VPC private subnets.
- Point `DATABASE_URL` to RDS:
  ```env
  DATABASE_URL=postgresql://<username>:<password>@<rds-endpoint>:5432/<dbname>
  ```

### 2. File Storage (AWS S3)
- Create a private Amazon S3 bucket (e.g., `my-job-tracker-resumes`).
- Enable default SSE-S3 encryption and block all public access.

### 3. Compute & Security (AWS EC2 & IAM)
- Launch an EC2 instance (Amazon Linux 2023 or Ubuntu 22.04) running Docker.
- Attach an **IAM Instance Profile** granting S3 permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ],
        "Resource": "arn:aws:s3:::my-job-tracker-resumes/*"
      }
    ]
  }
  ```
- **Zero hardcoded credentials**: The backend automatically leverages AWS SDK credential provider chain (IAM instance role) without needing `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`.

---

## 8. Out of Scope (v1)

As documented in section 8 of the technical specification:
- Refresh tokens / token revocation (frontend redirects to `/login` on token expiry)
- Multiple resumes per single application
- Email verification / password reset workflows
- Role-based access control (RBAC - single role only)
- Rate limiting
