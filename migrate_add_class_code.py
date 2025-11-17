"""
Migration script to add class_code column to existing classes table.
This script will:
1. Add the class_code column to existing classes
2. Generate unique codes for all existing classes
3. Handle the case where the column already exists
"""
import sqlite3
import os
import sys
from secrets import choice
from string import ascii_uppercase, digits

def generate_class_code(cursor):
    """Generate a unique 6-character alphanumeric class code"""
    while True:
        code = ''.join(choice(ascii_uppercase + digits) for _ in range(6))
        # Check if code already exists
        cursor.execute("SELECT COUNT(*) FROM classes WHERE class_code = ?", (code,))
        if cursor.fetchone()[0] == 0:
            return code

def migrate_database(db_path):
    """Add class_code column to classes table if it doesn't exist"""
    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if class_code column already exists
        cursor.execute("PRAGMA table_info(classes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'class_code' in columns:
            print("SUCCESS: class_code column already exists. No migration needed.")
            conn.close()
            return True
        
        print("Adding class_code column to classes table...")
        
        # Add the column (nullable first, then we'll populate it)
        cursor.execute("ALTER TABLE classes ADD COLUMN class_code VARCHAR(6)")
        print("SUCCESS: Column added successfully")
        
        # Get all existing classes
        cursor.execute("SELECT id FROM classes")
        class_ids = [row[0] for row in cursor.fetchall()]
        
        if class_ids:
            print(f"Generating class codes for {len(class_ids)} existing classes...")
            
            # Generate and assign codes to each class
            for class_id in class_ids:
                code = generate_class_code(cursor)
                cursor.execute("UPDATE classes SET class_code = ? WHERE id = ?", (code, class_id))
                print(f"   Class ID {class_id}: {code}")
            
            # Make the column NOT NULL and add unique constraint
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            print("Adding NOT NULL and UNIQUE constraints...")
            
            # Get all data from classes table
            cursor.execute("""
                SELECT id, name, description, teacher_id, created_at, class_code
                FROM classes
            """)
            classes_data = cursor.fetchall()
            
            # Get foreign key constraints
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='classes'")
            old_sql = cursor.fetchone()[0]
            
            # Drop old table
            cursor.execute("DROP TABLE classes")
            
            # Create new table with class_code as NOT NULL and UNIQUE
            cursor.execute("""
                CREATE TABLE classes (
                    id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    class_code VARCHAR(6) NOT NULL UNIQUE,
                    teacher_id INTEGER,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY(teacher_id) REFERENCES teachers (id) ON DELETE SET NULL
                )
            """)
            
            # Recreate index
            cursor.execute("CREATE INDEX ix_classes_teacher_id ON classes(teacher_id)")
            cursor.execute("CREATE INDEX ix_classes_class_code ON classes(class_code)")
            
            # Reinsert all data
            for class_data in classes_data:
                cursor.execute("""
                    INSERT INTO classes (id, name, description, teacher_id, created_at, class_code)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, class_data)
            
            print("SUCCESS: Constraints added successfully")
        
        conn.commit()
        print("SUCCESS: Migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Migration failed: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    # Get database path from config or use default
    db_path = "instance/database.db"
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"Migrating database: {db_path}")
    print("=" * 50)
    
    success = migrate_database(db_path)
    
    if success:
        print("=" * 50)
        print("SUCCESS: Migration completed! You can now run the app.")
    else:
        print("=" * 50)
        print("ERROR: Migration failed. Please check the errors above.")
        sys.exit(1)

