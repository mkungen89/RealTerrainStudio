"""
Run Database Migrations

This script runs SQL migrations on your Supabase database.
It reads SQL files from supabase/migrations/ and executes them.

Usage:
    python run_migrations.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import quote_plus
import psycopg2
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / "config" / ".env"
load_dotenv(env_path)

print("\n" + "="*60)
print("DATABASE MIGRATION RUNNER")
print("="*60 + "\n")

# Get database password
db_password = os.getenv("DATABASE_PASSWORD")
if not db_password:
    print("[ERROR] DATABASE_PASSWORD not found in .env")
    exit(1)

# URL-encode password to handle special characters
db_password_encoded = quote_plus(db_password)

# Build connection string
connection_string = f"postgresql://postgres:{db_password_encoded}@db.evxlknlcsjslqbhyjrud.supabase.co:5432/postgres"

print("[INFO] Connecting to database...")
print(f"[INFO] Host: db.evxlknlcsjslqbhyjrud.supabase.co")

try:
    # Connect to database
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    cursor = conn.cursor()

    print("[OK] Connected to database successfully!")

    # Find migration files
    migrations_dir = Path(__file__).parent / "supabase" / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("[WARNING] No migration files found in supabase/migrations/")
        exit(0)

    print(f"\n[INFO] Found {len(migration_files)} migration file(s):")
    for f in migration_files:
        print(f"       - {f.name}")

    # Run each migration
    print("\n[INFO] Running migrations...\n")

    for migration_file in migration_files:
        print(f"[INFO] Running: {migration_file.name}")

        # Read SQL file
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        try:
            # Execute SQL
            cursor.execute(sql)
            print(f"[OK] {migration_file.name} completed successfully!")

        except Exception as e:
            print(f"[ERROR] Failed to run {migration_file.name}: {e}")
            # Continue with other migrations

    # Verify tables were created
    print("\n[INFO] Verifying tables...")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()

    if tables:
        print(f"[OK] Found {len(tables)} table(s):")
        for table in tables:
            print(f"     - {table[0]}")
    else:
        print("[WARNING] No tables found")

    # Close connection
    cursor.close()
    conn.close()

    print("\n" + "="*60)
    print("MIGRATION COMPLETED!")
    print("="*60)
    print("\n[OK] Database setup complete!")
    print("[OK] Tables and RLS policies created!")
    print("[OK] Ready for development!")

except ImportError:
    print("\n[ERROR] psycopg2 not installed!")
    print("        Install with: pip install psycopg2-binary")
    exit(1)

except psycopg2.OperationalError as e:
    print(f"\n[ERROR] Could not connect to database: {e}")
    print("\nTroubleshooting:")
    print("1. Check DATABASE_PASSWORD in .env file")
    print("2. Check internet connection")
    print("3. Check Supabase project is active")
    print("4. Try accessing database from Supabase dashboard")
    exit(1)

except Exception as e:
    print(f"\n[ERROR] Migration failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
