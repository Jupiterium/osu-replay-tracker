import requests
import json
import sys
import os
import re

OSU_USER_ID = "13764890"
NTFY_TOPIC = "osu_jupiterium_replay_count" # Replace with your topic
STATE_FILE = "state.json"

def main():
    # Fetch profile page
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(f"https://osu.ppy.sh/users/{13764890}/osu", headers=headers)

    # Extract the replay count from the page's internal JSON payload
    match = re.search(r'"replays_watched_by_others"\s*:\s*(\d+)', response.text)
    if not match:
        print("Failed to find replay data on the page.")
        sys.exit(1)

    current_replays = int(match.group(1))
    old_replays = 0

    # Read the previous count if the state file exists
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            old_replays = data.get("replays", 0)

    # Compare and notify
    if current_replays > old_replays:
        diff = current_replays - old_replays
        message = f"📈 Replay count increased by {diff}!\nTotal views: {current_replays}"
        
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode('utf-8'), 
                      headers={"Title": "osu! Replay Tracker"})
        
        # Save the new state
        with open(STATE_FILE, "w") as f:
            json.dump({"replays": current_replays}, f)
        print(f"Updated count to {current_replays}.")
    else:
        print(f"No change. Count remains at {current_replays}.")

if __name__ == "__main__":
    main()
