# Database Schema Update

## Issue
Your database has an old schema and is missing new columns like `users.created_at`.

## Solution

You have 3 options to fix this:

### Option 1: Delete Database File (Easiest)
1. Stop the Flask app if it's running (Ctrl+C)
2. Delete the database file:
   ```powershell
   Remove-Item "instance\database.db" -Force
   ```
3. Run the app again:
   ```bash
   python app.py
   ```
   The database will be recreated automatically with the new schema.

### Option 2: Use Environment Variable
1. Stop the Flask app if it's running
2. Run with RECREATE_DB flag:
   ```powershell
   $env:RECREATE_DB='true'
   python app.py
   ```
   This will drop all tables and recreate them.

### Option 3: Run the Fix Script
```bash
python fix_database.py
```
Then run the app normally:
```bash
python app.py
```

## What Changed

The database schema was updated with:
- ✅ `users.created_at` column
- ✅ `students.first_name`, `last_name`, `created_at` columns
- ✅ `teachers.first_name`, `last_name`, `created_at` columns
- ✅ `classes.description`, `created_at` columns
- ✅ `assignments.class_id` (changed from `student_id`)
- ✅ New `submissions` table

## ⚠️ WARNING
Recreating the database will DELETE ALL YOUR DATA. Make sure to backup if needed!

