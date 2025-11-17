"""
Database Migration and Fix Script

This script helps fix database schema issues by either:
1. Recreating the database (if RECREATE_DB=true)
2. Running migration to add missing columns (if MIGRATE=true)
3. Or just checking the database status

Usage:
    python fix_database.py                    # Check database status
    python fix_database.py --recreate         # Recreate database (deletes all data)
    python fix_database.py --migrate          # Run migration to add class_code
"""
import os
import sys

def recreate_database():
    """Recreate the database by setting RECREATE_DB environment variable"""
    print("Setting up database recreation...")
    os.environ['RECREATE_DB'] = 'true'
    
    # Import app to trigger database recreation
    try:
        from app import app
        with app.app_context():
            from extensions import db
            db.create_all()
        print("SUCCESS: Database recreated successfully!")
        return True
    except Exception as e:
        print(f"ERROR: Error recreating database: {str(e)}")
        return False

def migrate_database():
    """Run migration to add class_code column"""
    print("Running migration to add class_code column...")
    try:
        from migrate_add_class_code import migrate_database
        db_path = "instance/database.db"
        return migrate_database(db_path)
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        return False

def check_database():
    """Check database status"""
    db_path = "instance/database.db"
    
    if not os.path.exists(db_path):
        print("INFO: Database file does not exist. It will be created on first app run.")
        return
    
    print(f"Checking database: {db_path}")
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if classes table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")
        if not cursor.fetchone():
            print("ERROR: Classes table does not exist. Database needs to be recreated.")
            conn.close()
            return
        
        # Check if class_code column exists
        cursor.execute("PRAGMA table_info(classes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'class_code' in columns:
            print("SUCCESS: Database schema is up to date. class_code column exists.")
        else:
            print("WARNING: Database schema is outdated. class_code column is missing.")
            print("   Run: python fix_database.py --migrate")
            print("   Or: python fix_database.py --recreate (will delete all data)")
        
        conn.close()
    except Exception as e:
        print(f"ERROR: Error checking database: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--recreate':
            print("=" * 60)
            print("WARNING: This will DELETE ALL DATA in the database!")
            print("=" * 60)
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() == 'yes':
                recreate_database()
            else:
                print("Cancelled.")
        elif sys.argv[1] == '--migrate':
            migrate_database()
        else:
            print("Usage:")
            print("  python fix_database.py           # Check database status")
            print("  python fix_database.py --recreate  # Recreate database (deletes all data)")
            print("  python fix_database.py --migrate    # Run migration to add class_code")
    else:
        check_database()

