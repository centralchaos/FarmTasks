#!/usr/bin/env python3
import os
import subprocess
import shutil
import time

def run_command(command, description):
    print(f"\n=== {description} ===")
    try:
        subprocess.run(command, shell=True, check=True)
        print("✓ Success")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        return False
    return True

def main():
    # Stop and remove Docker containers and volumes
    print("\n🧹 Resetting Docker environment...")
    run_command("docker-compose down -v", "Stopping and removing containers and volumes")
    
    # Remove instance folder
    print("\n🗑️ Cleaning up files...")
    if os.path.exists('instance'):
        try:
            # First try to make files writable
            for root, dirs, files in os.walk('instance'):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, 0o666)  # Make file writable
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    os.chmod(dir_path, 0o777)  # Make directory writable
            
            # Try regular removal first
            try:
                shutil.rmtree('instance')
                print("✓ Removed instance folder")
            except:
                # If regular removal fails, try force remove with sudo
                run_command("sudo rm -rf instance", "Force removing instance folder")
        except PermissionError:
            print("! Permission denied. Try running the script with sudo")
            return
    
    # Remove SQLite databases
    for db_file in os.listdir('.'):
        if db_file.endswith('.db'):
            os.remove(db_file)
            print(f"✓ Removed {db_file}")
    
    # Clean __pycache__
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))
                print(f"✓ Removed {os.path.join(root, d)}")
    
    # Start Docker containers
    print("\n🚀 Starting fresh Docker environment...")
    run_command("docker-compose up -d", "Starting Docker containers")
    
    # Wait for PostgreSQL to be ready
    print("\n⏳ Waiting for PostgreSQL to be ready...")
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        try:
            result = subprocess.run(
                "docker-compose exec db pg_isready -U farmtasks_user -d farmtasks_data",
                shell=True,
                capture_output=True
            )
            if result.returncode == 0:
                print("✓ PostgreSQL is ready")
                break
        except:
            pass
        attempt += 1
        time.sleep(1)
        print(".", end="", flush=True)
    
    print("\n\n✨ Reset complete! You can now:")
    print("1. Run 'flask run'")
    print("2. Visit http://localhost:5000")
    print("3. Complete the installation process")

if __name__ == "__main__":
    main() 