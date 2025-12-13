"""
Run Database Migrations via Supabase API

This script runs SQL migrations using the Supabase REST API.
Since direct PostgreSQL connection may have network issues,
this uses the Supabase client which we've already tested.

Usage:
    python run_migrations_api.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / "config" / ".env"
load_dotenv(env_path)

print("\n" + "="*60)
print("DATABASE MIGRATION RUNNER (API)")
print("="*60 + "\n")

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERROR] Supabase credentials not found in .env")
    exit(1)

print("[INFO] Connecting to Supabase...")

try:
    # Create admin client with service role key
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("[OK] Connected successfully!")

    # Find migration files
    migrations_dir = Path(__file__).parent / "supabase" / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("[WARNING] No migration files found in supabase/migrations/")
        exit(0)

    print(f"\n[INFO] Found {len(migration_files)} migration file(s):")
    for f in migration_files:
        print(f"       - {f.name}")

    print("\n[INFO] To run these migrations, please follow these steps:")
    print("="*60)
    print("\nOPTION 1: Run in Supabase Dashboard (Recommended)")
    print("-" * 60)
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project: RTS_APP")
    print("3. Click on 'SQL Editor' in the left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy the SQL from the migration file below")
    print("6. Paste into the editor")
    print("7. Click 'Run' or press Ctrl+Enter")
    print()

    # Read and display the first migration
    if migration_files:
        first_migration = migration_files[0]
        print(f"\nMigration file: {first_migration.name}")
        print("="*60)

        with open(first_migration, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(sql_content)
        print("="*60)

    print("\n[INFO] After running the SQL, come back and we'll verify!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)
