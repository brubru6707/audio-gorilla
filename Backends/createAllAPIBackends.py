import subprocess
import sys

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

def run_scripts():
    print("--- Starting script execution ---")
    
    for script in scripts_to_run:
        print(f"\n>>> Running script: {script}")
        try:
            result = subprocess.run(
                [sys.executable, script], 
                check=True, 
                capture_output=True, 
                text=True
            )
            
            print(f"--- Output of {script} ---")
            print(result.stdout)
            print(f"--- End of {script} output ---")
            
            print(f">>> Successfully finished: {script}")

        except FileNotFoundError:
            print(f"!!! ERROR: The file '{script}' was not found. Skipping.")
        
        except subprocess.CalledProcessError as e:
            print(f"!!! ERROR: An error occurred while running '{script}'.")
            print(f"--- Error output for {script} ---")
            print(e.stderr)
            print(f"--- End of {script} error output ---")
            
        except Exception as e:
            print(f"!!! An unexpected error occurred with {script}: {e}")

    print("\n--- All scripts have been processed. ---")

if __name__ == "__main__":
    run_scripts()
