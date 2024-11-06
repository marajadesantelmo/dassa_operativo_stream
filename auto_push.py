import os
import subprocess
import time

# Define the directory where your CSV files are stored
local_directory = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/data'
repo_directory = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream'

# Function to check for changes in the directory
def check_changes():
    try:
        # Run git status to check for changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_directory,
            capture_output=True,
            text=True
        )
        # If the result is empty, no changes
        return len(result.stdout.strip()) > 0
    except Exception as e:
        print(f"Error checking for changes: {e}")
        return False

# Function to push changes to GitHub
def commit_and_push():
    try:
        # Stage all changes
        subprocess.run(['git', 'add', '.'], cwd=repo_directory)
        
        # Commit the changes
        subprocess.run(['git', 'commit', '-m', '"Update automatico de datos v2"'], cwd=repo_directory)
        
        # Push to GitHub
        subprocess.run(['git', 'push'], cwd=repo_directory)
        print("Changes pushed to GitHub")
    except Exception as e:
        print(f"Error pushing changes: {e}")

# Main loop to check and push changes every 5 minutes
def main():
    while True:
        if check_changes():
            print("Changes detected, pushing to GitHub...")
            commit_and_push()
        else:
            print("No changes detected.")
        
        # Wait for 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    main()
