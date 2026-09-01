import requests
import json
import sys
import os

OSU_USER_ID = "13764890"
NTFY_TOPIC = "osu_jupiterium_replay_tracker" # Replace with your ntfy topic
STATE_FILE = "state.json"

CLIENT_ID = os.environ.get("OSU_CLIENT_ID")
CLIENT_SECRET = os.environ.get("OSU_CLIENT_SECRET")

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Missing OSU_CLIENT_ID or OSU_CLIENT_SECRET environment variables.")
        sys.exit(1)

    # 1. Authenticate with osu! API v2
    token_response = requests.post("https://osu.ppy.sh/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "public"
    })

    if token_response.status_code != 200:
        print("Failed to authenticate with osu! API.")
        sys.exit(1)

    token = token_response.json().get("access_token")

    # 2. Fetch User Data
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    user_response = requests.get(f"https://osu.ppy.sh/api/v2/users/{OSU_USER_ID}/osu", headers=headers)
    
    if user_response.status_code != 200:
        print("Failed to fetch user data from API.")
        sys.exit(1)

    user_data = user_response.json()
    current_replays = user_data.get("statistics", {}).get("replays_watched_by_others")

    if current_replays is None:
        print("Failed to find replay data in API response.")
        sys.exit(1)

    # 3. Compare and Notify
    old_replays = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            old_replays = data.get("replays", 0)

    if current_replays > old_replays:
        diff = current_replays - old_replays
        message = f"📈 Replay count increased by {diff}!\nTotal views: {current_replays}"
        
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode('utf-8'), 
                      headers={"Title": "osu! Replay Tracker"})
        
        with open(STATE_FILE, "w") as f:
            json.dump({"replays": current_replays}, f)
        print(f"Updated count to {current_replays}.")
    else:
        print(f"No change. Count remains at {current_replays}.")

if __name__ == "__main__":
    main()
