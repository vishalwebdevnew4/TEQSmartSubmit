# TEQSmartSubmit - Desktop Application

A Python desktop application for managing automated form submissions with PostgreSQL database.

## Quick Start

### Option 1: Automated Setup (Recommended)

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL:**
   - Create a database named `teqsmartsubmit`
   - Set environment variable:
     
     **Windows (PowerShell):**
     ```powershell
     $env:DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/teqsmartsubmit"
     ```
     
     **Linux/Mac:**
     ```bash
     export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/teqsmartsubmit"
     ```

3. **Run database migrations:**
   
   **Windows (PowerShell):**
   ```powershell
   cd backend; python -m alembic upgrade head; cd ..
   ```
   
   Or use the migration script:
   ```powershell
   .\run_migrations.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   cd backend && alembic upgrade head && cd ..
   ```

4. **Create an admin user:**
   ```bash
   python create_admin.py admin yourpassword
   ```

5. **Run the application:**
   
   **Windows (PowerShell):**
   ```powershell
   python run.py
   ```
   
   **Linux/Mac:**
   ```bash
   python run.py
   ```
   
   Or use the alternative entry point:
   ```bash
   python main.py
   ```

## Features

- **Desktop GUI**: Native desktop application with tkinter
- **PostgreSQL Database**: Full database integration
- **Domain Management**: Add, edit, and manage domains
- **Template Management**: Create form templates
- **Submission Logs**: View automation history
- **Dashboard**: Statistics and activity overview

## Project Structure

```
├── app/
│   ├── gui/              # GUI components
│   │   ├── main_window.py
│   │   ├── login.py
│   │   ├── dashboard.py
│   │   ├── domains.py
│   │   ├── templates.py
│   │   ├── logs.py
│   │   └── settings.py
│   └── db.py             # Database connection
├── backend/
│   └── app/               # Backend models and logic
│       ├── db/
│       ├── core/
│       └── ...
├── automation/            # Automation scripts
├── main.py               # Application entry point
├── create_admin.py       # Admin user creation script
└── requirements.txt     # Python dependencies
```

## Database Configuration

Set `DATABASE_URL` or `TEQ_DATABASE_URL` environment variable:
```
postgresql+asyncpg://username:password@localhost:5432/teqsmartsubmit
```

## Requirements

- Python 3.10+
- PostgreSQL 12+
- tkinter (usually included with Python)

## Notes

- The application uses async database operations with SQLAlchemy
- All database models are in `backend/app/db/models/`
- Authentication uses bcrypt password hashing
- The GUI uses tkinter (built into Python, no extra dependencies)
