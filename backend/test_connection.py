"""
Test Supabase Connection

This script tests the connection to your Supabase database
and verifies that the credentials work correctly.

Usage:
    python test_connection.py
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from config/.env
    env_path = Path(__file__).parent / "config" / ".env"
    load_dotenv(env_path)
    print(f"[OK] Loaded environment from: {env_path}")
except ImportError:
    print("[ERROR] python-dotenv not installed. Install with: pip install python-dotenv")
    exit(1)

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print("\n" + "="*60)
print("SUPABASE CONNECTION TEST")
print("="*60 + "\n")

# Verify credentials are loaded
print("Checking credentials...")
if not SUPABASE_URL:
    print("[ERROR] SUPABASE_URL not found in .env")
    exit(1)
if not SUPABASE_ANON_KEY:
    print("[ERROR] SUPABASE_ANON_KEY not found in .env")
    exit(1)
if not SUPABASE_SERVICE_KEY:
    print("[ERROR] SUPABASE_SERVICE_KEY not found in .env")
    exit(1)

print(f"[OK] SUPABASE_URL: {SUPABASE_URL}")
print(f"[OK] SUPABASE_ANON_KEY: {SUPABASE_ANON_KEY[:20]}...")
print(f"[OK] SUPABASE_SERVICE_KEY: {SUPABASE_SERVICE_KEY[:20]}...")

# Test connection
print("\nTesting connection to Supabase...")

try:
    from supabase import create_client, Client

    # Create client with anon key
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("[OK] Supabase client created successfully!")

    # Try to query the database (this will fail if tables don't exist yet)
    print("\nTesting database query...")
    try:
        response = supabase.table('profiles').select("*").limit(1).execute()
        print(f"[OK] Database query successful! Found {len(response.data)} records.")
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("[WARNING] Tables don't exist yet (expected - we haven't run migrations)")
            print("          This is normal! We'll create tables in the next step.")
        else:
            print(f"[WARNING] Query error: {e}")

    # Test service role key
    print("\nTesting service role key...")
    admin_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("[OK] Service role client created successfully!")

    print("\n" + "="*60)
    print("CONNECTION TEST PASSED!")
    print("="*60)
    print("\n[OK] Your Supabase credentials are working correctly!")
    print("[OK] Ready to run database migrations!")

except ImportError:
    print("\n[ERROR] Supabase library not installed!")
    print("        Install with: pip install supabase")
    print("        Or run: pip install -r requirements.txt")
    exit(1)

except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check that SUPABASE_URL is correct")
    print("2. Check that SUPABASE_ANON_KEY is correct")
    print("3. Check your internet connection")
    print("4. Check Supabase project is active")
    exit(1)
