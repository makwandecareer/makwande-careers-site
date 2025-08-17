# sync.py — run backend sync logic and exit (no server)
import sys
import main

if __name__ == "__main__":
    count = main.run_github_sync()
    print(f"Synced: {count}")
    sys.exit(0)
