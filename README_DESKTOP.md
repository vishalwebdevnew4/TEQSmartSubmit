# TEQSmartSubmit Desktop Application

A Python desktop application for managing automated form submissions with PostgreSQL database.

## Features

- **Desktop GUI**: Native desktop application built with tkinter
- **PostgreSQL Database**: Full database integration with SQLAlchemy
- **Domain Management**: Add, edit, and manage domains for automation
- **Template Management**: Create and manage form templates
- **Submission Logs**: View automation submission history
- **Dashboard**: Overview of automation statistics and recent activity

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   - Create a PostgreSQL database
   - Set environment variable:
     ```bash
     export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/teqsmartsubmit"
     ```
     Or on Windows:
     ```powershell
     $env:DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/teqsmartsubmit"
     ```

3. **Run database migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Create an admin user:**
   You can create an admin user using the API or directly in the database. For the desktop app, you'll need to create one via the database or use a script.

## Running the Application

```bash
python main.py
```

## Application Structure

```
app/
├── gui/              # GUI components
│   ├── main_window.py    # Main application window
│   ├── login.py          # Login dialog
│   ├── dashboard.py      # Dashboard view
│   ├── domains.py        # Domains management
│   ├── templates.py      # Templates management
│   ├── logs.py           # Logs viewer
│   └── settings.py       # Settings view
└── db.py             # Database connection

backend/
├── app/
│   ├── db/           # Database models and session
│   ├── core/          # Configuration and security
│   └── ...
```

## Database Configuration

The application uses PostgreSQL. Configure the connection via:

- Environment variable: `DATABASE_URL` or `TEQ_DATABASE_URL`
- Default: `postgresql+asyncpg://postgres:postgres@localhost:5432/teqsmartsubmit`

## Features

### Dashboard
- View total domains, active domains, forms found
- Success rate statistics
- Recent submission activity

### Domains Management
- Add new domains
- Edit existing domains
- Delete domains
- View domain status and contact page information

### Templates Management
- Create universal templates (work with all domains)
- Create domain-specific templates
- Edit field mappings (JSON format)
- Delete templates

### Logs Viewer
- View submission history
- Filter by status
- View detailed log messages

## Notes

- The application uses async database operations
- All database models are in `backend/app/db/models/`
- Authentication uses bcrypt password hashing
- The GUI uses tkinter (built into Python)

## Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL environment variable
- Verify database exists and user has permissions

**Import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that backend directory is accessible

