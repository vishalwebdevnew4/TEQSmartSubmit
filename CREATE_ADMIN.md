# Creating Admin User

## No Default Credentials

**There are NO default username/password combinations.** You must create an admin user first.

## How to Create Admin User

### Method 1: Command Line (Recommended)

```powershell
python create_admin.py admin yourpassword
```

**Example:**
```powershell
python create_admin.py admin admin123
```

This creates:
- **Username:** `admin`
- **Password:** `admin123`

### Method 2: Interactive (Password Hidden)

```powershell
python create_admin.py admin
```

This will prompt you to enter and confirm the password (hidden input).

### Method 3: With Email and Role

```powershell
python create_admin.py admin yourpassword --email admin@example.com --role admin
```

**Available roles:**
- `admin` - Full access
- `operator` - Limited access
- `viewer` - Read-only access

## Reset Password

If you forgot a password, reset it:

```powershell
python reset_admin_password.py admin newpassword
```

## Login

After creating an admin user, login at:
- **URL:** http://localhost:3000/login
- **Username:** (the username you created)
- **Password:** (the password you set)

## Troubleshooting

### Database Connection Error
Make sure PostgreSQL is running and `DATABASE_URL` is set correctly.

### User Already Exists
If you get "User already exists", either:
1. Use a different username
2. Reset the password: `python reset_admin_password.py admin newpassword`

### Import Errors
Make sure dependencies are installed:
```powershell
pip install -r requirements.txt
```

