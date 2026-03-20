"""
Initial setup script for R&D Platform.
Run this after a fresh clone to create database tables and a superuser.

Usage:
    python setup_project.py
"""
import subprocess
import sys
import os

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rnd_platform.settings')
    
    print("=" * 50)
    print("  R&D Platform - Initial Setup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    print("\n[1/3] Installing dependencies...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Step 2: Run migrations
    print("\n[2/3] Running database migrations...")
    subprocess.check_call([sys.executable, 'manage.py', 'migrate'])
    
    # Step 3: Create superuser
    print("\n[3/3] Creating superuser...")
    print("  (If you already have one, press Ctrl+C to skip)")
    try:
        subprocess.check_call([sys.executable, 'manage.py', 'createsuperuser'])
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        print("  Skipped superuser creation.")
    
    print("\n" + "=" * 50)
    print("  Setup complete! Run the server with:")
    print("  python manage.py runserver")
    print("=" * 50)

if __name__ == '__main__':
    main()
