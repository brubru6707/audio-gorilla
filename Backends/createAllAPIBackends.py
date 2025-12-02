

import subprocess
import sys
import os

# Get the current directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the backends directory (same directory as this script)
backends_dir = current_dir

scripts_to_run = [
    "createAmazonBackend.py",
    "createCommuniLinkBackend.py",
    "createGmailBackend.py",
    "createGoogleCalendarBackend.py",
    "createGoogleDriveBackend.py",
    "createSimpleNotesBackend.py",
    "createSmartThingsBackend.py",
    "createSpotifyBackends.py",
    "createTeslaBackend.py",
    "createVenmoBackend.py",
    "createXBackend.py",
    "createYouTubeBackend.py",
]

# NOTE: For more granular control (updating specific sections instead of replacing entire backends),
# use the updateBackends.py script instead of this one.

def run_scripts():
    print("--- Starting script execution ---")
    print(f"Running from directory: {backends_dir}")
    
    for script in scripts_to_run:
        # Create the full path to the script
        script_path = os.path.join(backends_dir, script)
        
        print(f"\n>>> Running script: {script_path}")
        
        # Check if the file exists before trying to run it
        if not os.path.exists(script_path):
            print(f"!!! ERROR: The file '{script_path}' was not found. Skipping.")
            continue
            
        try:
            result = subprocess.run(
                [sys.executable, script_path], 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=backends_dir  # Run from the backends directory
            )
            
            print(f"--- Output of {script} ---")
            print(result.stdout)
            if result.stderr:
                print(f"--- Error output for {script} ---")
                print(result.stderr)
                print(f"--- End of {script} error output ---")
            else:
                print(f"--- End of {script} output ---")
            
            print(f">>> Successfully finished: {script}")

        except subprocess.CalledProcessError as e:
            print(f"!!! ERROR: An error occurred while running '{script_path}'.")
            print(f"Return code: {e.returncode}")
            if e.stdout:
                print(f"--- Output for {script} ---")
                print(e.stdout)
            if e.stderr:
                print(f"--- Error output for {script} ---")
                print(e.stderr)
                print(f"--- End of {script} error output ---")
            
        except Exception as e:
            print(f"!!! An unexpected error occurred with {script_path}: {e}")

    print("\n--- All scripts have been processed. ---")

if __name__ == "__main__":
    run_scripts()